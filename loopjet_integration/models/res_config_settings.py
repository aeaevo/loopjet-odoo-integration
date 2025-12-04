# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    loopjet_api_key = fields.Char(
        string='Loopjet API Key',
        config_parameter='loopjet.api_key',
        help='Your Loopjet API authentication key. Get it from your Loopjet account settings.'
    )
    
    loopjet_default_language = fields.Selection(
        [
            ('en', 'English'),
            ('de', 'German'),
            ('es', 'Spanish'),
            ('fr', 'French'),
            ('it', 'Italian'),
            ('pt', 'Portuguese'),
            ('nl', 'Dutch'),
            ('pl', 'Polish'),
        ],
        string='Default Language',
        config_parameter='loopjet.default_language',
        default='en',
        help='Default language for AI-generated estimates.'
    )

    @api.model
    def get_loopjet_api_headers(self):
        """Get headers for Loopjet API requests."""
        api_key = self.env['ir.config_parameter'].sudo().get_param('loopjet.api_key')
        if not api_key:
            raise ValueError('Loopjet API key not configured. Please configure it in Settings > General Settings > Loopjet Integration.')
        
        return {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        }
    
    @api.model
    def get_loopjet_api_url(self):
        """Get Loopjet API base URL - hardcoded to production server."""
        return 'https://loopjet-api.fly.dev'
    
    def action_sync_all_products(self):
        """Batch sync all products to Loopjet."""
        self.ensure_one()
        
        # Check if API key is configured
        api_key = self.env['ir.config_parameter'].sudo().get_param('loopjet.api_key')
        if not api_key:
            raise ValueError('Please configure your Loopjet API key before syncing products.')
        
        # Get all products (both product.product and product.template)
        products = self.env['product.template'].search([
            ('sale_ok', '=', True),  # Only products that can be sold
        ])
        
        if not products:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'No Products Found',
                    'message': 'No products available to sync.',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        # Prepare products for batch sync
        import requests
        
        api_url = 'https://loopjet-api.fly.dev'
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        }
        
        # Get company currency as fallback
        company_currency = self.env.company.currency_id.name if self.env.company.currency_id else 'EUR'
        
        product_list = []
        for product in products:
            # Currency fallback: product currency → company currency → EUR
            product_currency = product.currency_id.name if product.currency_id else company_currency
            
            # Unit fallback: product UoM → 'unit'
            product_unit = product.uom_id.name if product.uom_id else 'unit'
            
            product_list.append({
                'name': product.name,
                'description': product.description_sale or product.description or '',
                'is_service': product.type == 'service',
                'price': float(product.list_price),
                'currency': product_currency,
                'unit': product_unit,
            })
        
        # Use batch import endpoint with upsert to prevent duplicates
        try:
            url = f"{api_url}/api/v1/batch/products/batch"
            response = requests.post(url, json={'products': product_list, 'upsert': True}, headers=headers, timeout=60)
            
            if response.status_code in [200, 201]:
                result = response.json()
                success_count = result.get('created', 0) + result.get('updated', 0)
                error_count = result.get('failed', 0)
            else:
                success_count = 0
                error_count = len(product_list)
                _logger.error(f"Batch product sync failed: {response.text}")
        except Exception as e:
            success_count = 0
            error_count = len(product_list)
            _logger.error(f"Error in batch product sync: {str(e)}")
        
        # Show notification with results
        if error_count == 0:
            message = f'Successfully synced {success_count} products to Loopjet!'
            notification_type = 'success'
        else:
            message = f'Synced {success_count} products. {error_count} failed. Check logs for details.'
            notification_type = 'warning'
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Product Sync Complete',
                'message': message,
                'type': notification_type,
                'sticky': False,
            }
        }
    
    def action_sync_all_contacts(self):
        """Batch sync all contacts to Loopjet."""
        self.ensure_one()
        
        # Check if API key is configured
        api_key = self.env['ir.config_parameter'].sudo().get_param('loopjet.api_key')
        if not api_key:
            raise ValueError('Please configure your Loopjet API key before syncing contacts.')
        
        # Get all partners/contacts (customers and vendors)
        contacts = self.env['res.partner'].search([
            '|',
            ('customer_rank', '>', 0),  # Customers
            ('supplier_rank', '>', 0),  # Suppliers
        ])
        
        if not contacts:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'No Contacts Found',
                    'message': 'No contacts available to sync.',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        # Prepare contacts for batch sync
        import requests
        
        api_url = 'https://loopjet-api.fly.dev'
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        }
        
        contact_list = []
        for contact in contacts:
            contact_data = {
                'name': contact.name,
                'email': contact.email or None,
                'phone': contact.phone or None,
                'address_line1': contact.street or None,
                'address_line2': contact.street2 or None,
                'city': contact.city or None,
                'state': contact.state_id.name if contact.state_id else None,
                'postal_code': contact.zip or None,
                'country': contact.country_id.name if contact.country_id else None,
                'company': contact.commercial_company_name or contact.name if contact.is_company else None,
                'tax_id': contact.vat or None,
                'website': contact.website or None,
                'notes': contact.comment or None,
                'type': 'customer' if contact.customer_rank > 0 else 'vendor',
            }
            
            # Remove None values
            contact_data = {k: v for k, v in contact_data.items() if v is not None}
            contact_list.append(contact_data)
        
        # Use batch import endpoint with upsert
        try:
            url = f"{api_url}/api/v1/batch/contacts/batch"
            response = requests.post(url, json={'contacts': contact_list, 'upsert': True}, headers=headers, timeout=60)
            
            if response.status_code in [200, 201]:
                result = response.json()
                success_count = result.get('created', 0) + result.get('updated', 0)
                error_count = result.get('failed', 0)
            else:
                success_count = 0
                error_count = len(contact_list)
                _logger.error(f"Batch contact sync failed: {response.text}")
        except Exception as e:
            success_count = 0
            error_count = len(contact_list)
            _logger.error(f"Error in batch contact sync: {str(e)}")
        
        # Show notification with results
        if error_count == 0:
            message = f'Successfully synced {success_count} contacts to Loopjet!'
            notification_type = 'success'
        else:
            message = f'Synced {success_count} contacts. {error_count} failed. Check logs for details.'
            notification_type = 'warning'
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Contact Sync Complete',
                'message': message,
                'type': notification_type,
                'sticky': False,
            }
        }
    
    def action_sync_all_invoices(self):
        """Batch sync all invoices to Loopjet."""
        self.ensure_one()
        
        # Check if API key is configured
        api_key = self.env['ir.config_parameter'].sudo().get_param('loopjet.api_key')
        if not api_key:
            raise ValueError('Please configure your Loopjet API key before syncing invoices.')
        
        # Get all invoices (account.move with type invoice)
        invoices = self.env['account.move'].search([
            ('move_type', 'in', ['out_invoice', 'out_refund']),
            ('state', '!=', 'cancel'),
        ], limit=100)  # Limit to 100 for performance
        
        if not invoices:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'No Invoices Found',
                    'message': 'No invoices available to sync.',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        # Sync via batch API
        import requests
        
        api_url = 'https://loopjet-api.fly.dev'
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        }
        
        # Get company currency as fallback
        company_currency = self.env.company.currency_id.name if self.env.company.currency_id else 'EUR'
        
        # Prepare batch data
        invoice_list = []
        for invoice in invoices:
            invoice_data = {
                'invoice_number': invoice.name,
                'customer_id': None,  # Will be matched by name
                'customer_info': {
                    'name': invoice.partner_id.name,
                    'email': invoice.partner_id.email,
                    'phone': invoice.partner_id.phone,
                },
                'issue_date': invoice.invoice_date.isoformat() if invoice.invoice_date else None,
                'due_date': invoice.invoice_date_due.isoformat() if invoice.invoice_date_due else None,
                'status': 'sent' if invoice.state == 'posted' else 'draft',
                'items': [],
                'subtotal': float(invoice.amount_untaxed),
                'total_tax': float(invoice.amount_tax),
                'total': float(invoice.amount_total),
                'external_id': str(invoice.id),
                'external_system': 'odoo',
            }
            
            # Add line items
            for line in invoice.invoice_line_ids:
                if line.product_id:
                    invoice_data['items'].append({
                        'name': line.product_id.name,
                        'description': line.name,
                        'quantity': line.quantity,
                        'unit_price': float(line.price_unit),
                        'unit': line.product_uom_id.name if line.product_uom_id else 'unit',
                        'currency': invoice.currency_id.name if invoice.currency_id else company_currency,
                    })
            
            invoice_list.append(invoice_data)
        
        # Use batch import endpoint
        try:
            url = f"{api_url}/api/v1/batch/invoices/batch"
            response = requests.post(url, json={'invoices': invoice_list}, headers=headers, timeout=60)
            
            if response.status_code in [200, 201]:
                result = response.json()
                success_count = result.get('created', 0) + result.get('updated', 0)
                message = f'Successfully synced {success_count} invoices to Loopjet!'
                notification_type = 'success'
            else:
                message = f'Failed to sync invoices. Error: {response.text[:200]}'
                notification_type = 'warning'
                
        except Exception as e:
            message = f'Error syncing invoices: {str(e)}'
            notification_type = 'danger'
            _logger.error(message)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Invoice Sync Complete',
                'message': message,
                'type': notification_type,
                'sticky': False,
            }
        }
    
    def action_sync_all_estimates(self):
        """Batch sync all estimates/quotations to Loopjet."""
        self.ensure_one()
        
        # Check if API key is configured
        api_key = self.env['ir.config_parameter'].sudo().get_param('loopjet.api_key')
        if not api_key:
            raise ValueError('Please configure your Loopjet API key before syncing estimates.')
        
        # Get all quotations (sale orders in quotation state)
        estimates = self.env['sale.order'].search([
            ('state', 'in', ['draft', 'sent']),
        ], limit=100)  # Limit to 100 for performance
        
        if not estimates:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'No Estimates Found',
                    'message': 'No quotations available to sync.',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        # Sync via batch API
        import requests
        from datetime import date
        
        api_url = 'https://loopjet-api.fly.dev'
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        }
        
        # Get company currency as fallback
        company_currency = self.env.company.currency_id.name if self.env.company.currency_id else 'EUR'
        
        # Prepare batch data
        estimate_list = []
        for estimate in estimates:
            estimate_data = {
                'estimate_number': estimate.name,
                'customer_id': None,  # Will be matched by name
                'customer_info': {
                    'name': estimate.partner_id.name,
                    'email': estimate.partner_id.email,
                    'phone': estimate.partner_id.phone,
                },
                'issue_date': estimate.date_order.date().isoformat() if estimate.date_order else date.today().isoformat(),
                'valid_until': estimate.validity_date.isoformat() if estimate.validity_date else None,
                'status': 'sent' if estimate.state == 'sent' else 'draft',
                'items': [],
                'subtotal': float(estimate.amount_untaxed),
                'total_tax': float(estimate.amount_tax),
                'total': float(estimate.amount_total),
                'external_id': str(estimate.id),
                'external_system': 'odoo',
            }
            
            # Add line items
            for line in estimate.order_line:
                if line.product_id:
                    # Get UOM (unit of measure) - field name varies by Odoo version
                    uom_name = 'unit'
                    if hasattr(line, 'product_uom') and line.product_uom:
                        uom_name = line.product_uom.name
                    elif hasattr(line, 'product_uom_id') and line.product_uom_id:
                        uom_name = line.product_uom_id.name
                    
                    estimate_data['items'].append({
                        'name': line.product_id.name,
                        'description': line.name,
                        'quantity': line.product_uom_qty if hasattr(line, 'product_uom_qty') else line.quantity,
                        'unit_price': float(line.price_unit),
                        'unit': uom_name,
                        'currency': estimate.currency_id.name if estimate.currency_id else company_currency,
                    })
            
            estimate_list.append(estimate_data)
        
        # Use batch import endpoint
        try:
            url = f"{api_url}/api/v1/batch/estimates/batch"
            response = requests.post(url, json={'estimates': estimate_list}, headers=headers, timeout=60)
            
            if response.status_code in [200, 201]:
                result = response.json()
                success_count = result.get('created', 0) + result.get('updated', 0)
                message = f'Successfully synced {success_count} quotations to Loopjet!'
                notification_type = 'success'
            else:
                message = f'Failed to sync quotations. Error: {response.text[:200]}'
                notification_type = 'warning'
                
        except Exception as e:
            message = f'Error syncing quotations: {str(e)}'
            notification_type = 'danger'
            _logger.error(message)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Quotation Sync Complete',
                'message': message,
                'type': notification_type,
                'sticky': False,
            }
        }

