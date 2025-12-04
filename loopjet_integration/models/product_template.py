# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests
import json
import logging

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    loopjet_product_id = fields.Char(
        string='Loopjet Product ID',
        readonly=True,
        help='UUID of this product in Loopjet system'
    )
    
    loopjet_synced = fields.Boolean(
        string='Synced to Loopjet',
        default=False,
        readonly=True,
        help='Whether this product has been synchronized to Loopjet'
    )
    
    loopjet_last_sync = fields.Datetime(
        string='Last Loopjet Sync',
        readonly=True,
        help='Last time this product was synced to Loopjet'
    )

    def sync_to_loopjet(self):
        """Sync this product to Loopjet."""
        for product in self:
            try:
                # Get API configuration
                api_key = self.env['ir.config_parameter'].sudo().get_param('loopjet.api_key')
                _logger.info(f"Retrieved API key: {api_key[:10] if api_key else 'NONE'}...")
                
                if not api_key:
                    raise ValueError('Loopjet API key not configured')
                
                api_url = 'https://loopjet-api.fly.dev'
                headers = {
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json',
                }
                
                _logger.info(f"Headers: {headers}")
                _logger.info(f"Syncing product {product.name} to Loopjet at {api_url}")
                
                # Prepare product data for Loopjet API
                # API expects is_service and handles transformation to database type field
                # Currency fallback: product currency → company currency → EUR
                company_currency = self.env.company.currency_id.name if self.env.company.currency_id else 'EUR'
                product_currency = product.currency_id.name if product.currency_id else company_currency
                
                # Unit fallback: product UoM → 'unit'
                product_unit = product.uom_id.name if product.uom_id else 'unit'
                
                product_data = {
                    'name': product.name,
                    'description': product.description_sale or product.description or '',
                    'is_service': product.type == 'service',
                    'price': float(product.list_price),
                    'currency': product_currency,
                    'unit': product_unit,
                }
                
                _logger.info(f"Product data: {product_data}")
                
                # If already synced, update; otherwise create
                if product.loopjet_product_id:
                    # Update existing product
                    url = f"{api_url}/api/v1/products/{product.loopjet_product_id}"
                    _logger.info(f"Updating product at {url}")
                    response = requests.put(url, json=product_data, headers=headers, timeout=30, allow_redirects=True)
                else:
                    # Create new product
                    url = f"{api_url}/api/v1/products/"  # Trailing slash important!
                    _logger.info(f"Creating product at {url}")
                    response = requests.post(url, json=product_data, headers=headers, timeout=30, allow_redirects=True)
                
                _logger.info(f"API Response: Status={response.status_code}, Body={response.text[:200]}")
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    product.write({
                        'loopjet_product_id': result.get('id'),
                        'loopjet_synced': True,
                        'loopjet_last_sync': fields.Datetime.now(),
                    })
                    _logger.info(f"Successfully synced product {product.name} to Loopjet (ID: {result.get('id')})")
                else:
                    error_msg = f"Failed to sync product {product.name}: HTTP {response.status_code} - {response.text}"
                    _logger.error(error_msg)
                    raise Exception(error_msg)
                    
            except Exception as e:
                error_msg = f"Error syncing product {product.name} to Loopjet: {str(e)}"
                _logger.error(error_msg)
                raise  # Re-raise to be caught by batch sync


