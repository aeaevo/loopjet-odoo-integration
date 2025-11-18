# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    loopjet_invoice_id = fields.Char(
        string='Loopjet Invoice ID',
        readonly=True,
        help='UUID of this invoice in Loopjet system'
    )
    
    loopjet_synced = fields.Boolean(
        string='Synced to Loopjet',
        default=False,
        readonly=True,
        help='Whether this invoice has been synchronized to Loopjet'
    )
    
    loopjet_last_sync = fields.Datetime(
        string='Last Loopjet Sync',
        readonly=True,
        help='Last time this invoice was synced to Loopjet'
    )

    def sync_to_loopjet(self):
        """Sync this invoice to Loopjet."""
        for invoice in self:
            # Only sync customer invoices, not bills or other types
            if invoice.move_type not in ['out_invoice', 'out_refund'] or invoice.state == 'cancel':
                continue
                
            try:
                # Get API configuration
                api_key = self.env['ir.config_parameter'].sudo().get_param('loopjet.api_key')
                if not api_key:
                    _logger.warning('Loopjet API key not configured, skipping invoice sync')
                    return
                
                api_url = 'https://loopjet-api.fly.dev'
                headers = {
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json',
                }
                
                # Prepare invoice data
                invoice_data = {
                    'invoice_number': invoice.name,
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
                        })
                
                # If already synced, update; otherwise create
                if invoice.loopjet_invoice_id:
                    url = f"{api_url}/api/v1/invoices/{invoice.loopjet_invoice_id}"
                    response = requests.put(url, json=invoice_data, headers=headers, timeout=30)
                else:
                    url = f"{api_url}/api/v1/invoices/"
                    response = requests.post(url, json=invoice_data, headers=headers, timeout=30)
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    invoice.write({
                        'loopjet_invoice_id': result.get('id'),
                        'loopjet_synced': True,
                        'loopjet_last_sync': fields.Datetime.now(),
                    })
                    _logger.info(f"Successfully synced invoice {invoice.name} to Loopjet")
                else:
                    _logger.error(f"Failed to sync invoice {invoice.name}: {response.text}")
                    
            except Exception as e:
                _logger.error(f"Error syncing invoice {invoice.name} to Loopjet: {str(e)}")


