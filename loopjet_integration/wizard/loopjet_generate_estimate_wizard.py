# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import requests
import json
import logging
from datetime import date

_logger = logging.getLogger(__name__)


class LoopjetGenerateEstimateWizard(models.TransientModel):
    _name = 'loopjet.generate.estimate.wizard'
    _description = 'Generate Estimate with Loopjet AI'

    lead_id = fields.Many2one(
        'crm.lead',
        string='Opportunity',
        required=True,
        readonly=True,
    )
    
    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
        related='lead_id.partner_id',
        readonly=True,
    )
    
    extracted_info = fields.Text(
        string='Extracted Information',
        readonly=True,
        help='Information extracted from the CRM deal that will be sent to Loopjet AI'
    )
    
    additional_instructions = fields.Text(
        string='Additional Instructions',
        help='Optional: Add specific instructions for the AI (e.g., "Include migration services", "Add training sessions")'
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('error', 'Error'),
    ], default='draft', readonly=True)
    
    error_message = fields.Text(
        string='Error Message',
        readonly=True,
    )
    
    estimate_preview = fields.Text(
        string='AI Response',
        readonly=True,
        help='Preview of the AI-generated estimate'
    )

    @api.model
    def default_get(self, fields_list):
        """Extract deal information when wizard opens."""
        res = super(LoopjetGenerateEstimateWizard, self).default_get(fields_list)
        
        if 'lead_id' in res and res['lead_id']:
            lead = self.env['crm.lead'].browse(res['lead_id'])
            if lead.exists():
                res['extracted_info'] = lead.extract_deal_information()
        
        return res

    def action_generate_estimate(self):
        """Call Loopjet API to generate estimate and create sale order."""
        self.ensure_one()
        
        # Validate that opportunity has a customer BEFORE calling API
        if not self.customer_id:
            raise UserError(_(
                'Customer Required\n\n'
                'This opportunity does not have a customer/partner linked.\n\n'
                'Please click Cancel, add a customer to the opportunity, and try again.'
            ))
        
        # Validate that products exist BEFORE syncing/generating
        products = self.env['product.template'].search([('sale_ok', '=', True)], limit=1)
        if not products:
            raise UserError(_(
                'No Products Available\n\n'
                'You need to create at least one product or service before generating AI estimates.\n\n'
                'Steps to fix:\n'
                '1. Go to Sales → Products → Products\n'
                '2. Create your products or services\n'
                '3. Return here and try again\n\n'
                'The AI needs your product catalog to generate accurate estimates.'
            ))
        
        # Show loading notification to user immediately (appears as soon as button is clicked)
        # This provides instant feedback while the AI processes (30s-2min)
        message = {
            'type': 'info',
            'title': 'Preparing & Syncing Data...',
            'message': '⏱️ Syncing products, contact, and relevant data to Loopjet before generating estimate. This usually takes 30 seconds to 2 minutes. Please wait...',
            'sticky': True,  # Stays visible until completed
        }
        self.env['bus.bus']._sendone(self.env.user.partner_id, 'notification', message)
        
        try:
            # Sync all products, services, customer contact, and related invoices/estimates
            # BEFORE generating AI estimate to ensure AI has latest data
            _logger.info(f"Starting automatic data sync for lead {self.lead_id.name}")
            self._sync_data_to_loopjet()
            _logger.info("Data sync completed, proceeding with AI estimate generation")
            
            # Get API configuration
            api_key = self.env['ir.config_parameter'].sudo().get_param('loopjet.api_key')
            if not api_key:
                raise UserError(_('Loopjet API key not configured. Please go to Settings > Loopjet Integration and add your API key.'))
            
            api_url = 'https://loopjet-api.fly.dev'
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
            }
            
            # Prepare request data
            user_input = self.extracted_info
            if self.additional_instructions:
                user_input += f"\n\nAdditional Instructions:\n{self.additional_instructions}"
            
            # Prepare customer contact data
            customer_contact_data = None
            if self.customer_id:
                customer_contact_data = {
                    'name': self.customer_id.name,
                    'email': self.customer_id.email or None,
                    'phone': self.customer_id.phone or None,
                    'address_line1': self.customer_id.street or None,
                    'address_line2': self.customer_id.street2 or None,
                    'city': self.customer_id.city or None,
                    'state': self.customer_id.state_id.name if self.customer_id.state_id else None,
                    'postal_code': self.customer_id.zip or None,
                    'country': self.customer_id.country_id.name if self.customer_id.country_id else None,
                    'company': self.customer_id.commercial_company_name or self.customer_id.name,
                    'website': self.customer_id.website or None,
                }
            
            request_data = {
                'user_input': user_input,
                'customer_name': self.customer_id.name if self.customer_id else None,
                'customer_contact_data': customer_contact_data,
                'allow_new_items': False,  # Always use existing products only
                'auto_save': False,  # We'll create the sale order in Odoo, not in Loopjet
            }
            
            # Get default language
            default_language = self.env['ir.config_parameter'].sudo().get_param('loopjet.default_language', 'en')
            
            _logger.info(f"Calling Loopjet API to generate estimate for lead {self.lead_id.name}")
            _logger.debug(f"Request data: {json.dumps(request_data, indent=2)}")
            
            # Call Loopjet API (increased timeout for complex AI requests)
            url = f"{api_url}/api/v1/ai/generate-estimate"
            response = requests.post(url, json=request_data, headers=headers, timeout=360)
            
            if response.status_code == 402:
                # Insufficient credits
                error_data = response.json()
                raise UserError(_(
                    'Insufficient Loopjet Credits\n\n'
                    f'{error_data.get("detail", {}).get("message", "You need more credits to generate estimates.")}\n\n'
                    f'Current balance: {error_data.get("detail", {}).get("balance", 0)} credits\n'
                    f'Required: {error_data.get("detail", {}).get("required", 0)} credits\n'
                    f'Shortfall: {error_data.get("detail", {}).get("shortfall", 0)} credits\n\n'
                    'Please purchase more credits in your Loopjet account.'
                ))
            
            if response.status_code == 400:
                # Handle validation errors (like no products available)
                try:
                    error_data = response.json()
                    if isinstance(error_data.get('detail'), dict):
                        # Structured error with helpful message
                        error_msg = error_data['detail'].get('message', str(error_data))
                    else:
                        error_msg = str(error_data.get('detail', response.text))
                except:
                    error_msg = response.text
                
                raise UserError(_(f'Cannot Generate Quotation\n\n{error_msg}'))
            
            if response.status_code not in [200, 201]:
                error_detail = response.json().get('detail', response.text) if response.headers.get('content-type', '').startswith('application/json') else response.text
                raise UserError(_(
                    f'Loopjet API Error (HTTP {response.status_code})\n\n'
                    f'{error_detail}'
                ))
            
            result = response.json()
            _logger.info(f"Received Loopjet API response with {len(result.get('items', []))} items")
            
            # Store preview
            preview_text = f"AI Reasoning:\n{result.get('reasoning', 'N/A')}\n\n"
            preview_text += f"Generated {len(result.get('items', []))} estimate items:\n"
            for idx, item in enumerate(result.get('items', []), 1):
                preview_text += f"{idx}. {item.get('name')} - Qty: {item.get('quantity')} x {item.get('unit_price')} = {item.get('quantity') * item.get('unit_price')}\n"
                if item.get('description'):
                    preview_text += f"   Description: {item.get('description')}\n"
            
            self.write({
                'estimate_preview': preview_text,
                'state': 'done',
            })
            
            # Create sale order
            sale_order = self._create_sale_order_from_loopjet_response(result)
            
            # Show success notification
            success_message = {
                'type': 'success',
                'title': '✅ Quotation Created!',
                'message': f'Successfully generated quotation {sale_order.name} with {len(result.get("items", []))} items.',
                'sticky': False,
            }
            self.env['bus.bus']._sendone(self.env.user.partner_id, 'notification', success_message)
            
            # Return action to view the created sale order
            return {
                'name': _('AI-Generated Quotation'),
                'type': 'ir.actions.act_window',
                'res_model': 'sale.order',
                'res_id': sale_order.id,
                'view_mode': 'form',
                'target': 'current',
            }
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to connect to Loopjet API: {str(e)}"
            _logger.error(error_msg)
            self.write({
                'state': 'error',
                'error_message': error_msg,
            })
            raise UserError(_(error_msg))
            
        except Exception as e:
            error_msg = f"Error generating estimate: {str(e)}"
            _logger.error(error_msg, exc_info=True)
            self.write({
                'state': 'error',
                'error_message': error_msg,
            })
            raise UserError(_(error_msg))

    def _create_sale_order_from_loopjet_response(self, loopjet_data):
        """
        Create Odoo sale order from Loopjet API response.
        
        Args:
            loopjet_data: Dictionary containing Loopjet API response
            
        Returns:
            sale.order: Created sale order
        """
        self.ensure_one()
        
        # Prepare sale order values (customer already validated in action_generate_estimate)
        sale_order_vals = {
            'partner_id': self.customer_id.id,
            'loopjet_generated': True,
            'loopjet_estimate_data': json.dumps(loopjet_data, indent=2),
            'loopjet_reasoning': loopjet_data.get('reasoning', ''),
            'note': loopjet_data.get('notes', ''),
            'date_order': fields.Datetime.now(),
        }
        
        # Add opportunity link using the correct field name for this Odoo version
        SaleOrder = self.env['sale.order']
        if 'opportunity_id' in SaleOrder._fields:
            sale_order_vals['opportunity_id'] = self.lead_id.id
        elif 'crm_lead_id' in SaleOrder._fields:
            sale_order_vals['crm_lead_id'] = self.lead_id.id
        
        # Create sale order
        sale_order = self.env['sale.order'].create(sale_order_vals)
        _logger.info(f"Created sale order {sale_order.name} from Loopjet estimate")
        
        # Create order lines from Loopjet items
        items = loopjet_data.get('items', [])
        for item_data in items:
            self._create_sale_order_line(sale_order, item_data)
        
        # Link sale order to lead (if the relationship field exists)
        if hasattr(self.lead_id, 'order_ids'):
            self.lead_id.order_ids = [(4, sale_order.id)]
        
        return sale_order

    def _create_sale_order_line(self, sale_order, item_data):
        """
        Create sale order line from Loopjet item data.
        
        Args:
            sale_order: sale.order record
            item_data: Dictionary containing item information from Loopjet
        """
        # Try to find matching product in Odoo
        product = None
        
        # First, try to match by Loopjet product_id
        if item_data.get('product_id'):
            product = self.env['product.product'].search([
                ('product_tmpl_id.loopjet_product_id', '=', item_data['product_id'])
            ], limit=1)
        
        # If not found, try to match by name
        if not product and item_data.get('name'):
            product = self.env['product.product'].search([
                ('name', '=ilike', item_data['name'])
            ], limit=1)
        
        # If still not found, create a new product
        if not product:
            product_vals = {
                'name': item_data['name'],
                'description_sale': item_data.get('description', ''),
                'list_price': item_data.get('unit_price', 0.0),
                'type': 'service',  # Default to service
                'loopjet_product_id': item_data.get('product_id'),
            }
            product = self.env['product.product'].create(product_vals)
            _logger.info(f"Created new product: {product.name}")
        
        # Calculate discount
        discount_percentage = item_data.get('discount_percentage', 0.0)
        
        # Calculate tax
        tax_rate = item_data.get('tax_rate', 0.0)
        tax_ids = []
        if tax_rate > 0:
            # Try to find matching tax
            tax = self.env['account.tax'].search([
                ('amount', '=', tax_rate),
                ('type_tax_use', '=', 'sale'),
                ('company_id', '=', sale_order.company_id.id),
            ], limit=1)
            if tax:
                tax_ids = [(6, 0, [tax.id])]
        
        # Create order line
        line_vals = {
            'order_id': sale_order.id,
            'product_id': product.id,
            'name': item_data.get('description') or item_data['name'],
            'product_uom_qty': item_data.get('quantity', 1.0),
            'price_unit': item_data.get('unit_price', 0.0),
            'discount': discount_percentage,
            'loopjet_item_id': item_data.get('id'),
        }
        
        # Add tax field using the correct field name for this Odoo version
        # Odoo 19 might use 'tax_ids' instead of 'tax_id'
        if 'tax_ids' in self.env['sale.order.line']._fields:
            line_vals['tax_ids'] = tax_ids
        elif 'tax_id' in self.env['sale.order.line']._fields:
            line_vals['tax_id'] = tax_ids
        
        self.env['sale.order.line'].create(line_vals)
        _logger.info(f"Created order line: {item_data['name']}")

    def action_retry(self):
        """Reset wizard to retry estimate generation."""
        self.write({
            'state': 'draft',
            'error_message': False,
            'estimate_preview': False,
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def _sync_data_to_loopjet(self):
        """
        Sync all relevant data to Loopjet before generating AI estimate.
        This includes:
        - All products/services
        - The customer contact
        - Related invoices and estimates for context
        """
        self.ensure_one()
        
        # Get API configuration
        api_key = self.env['ir.config_parameter'].sudo().get_param('loopjet.api_key')
        if not api_key:
            raise UserError(_('Loopjet API key not configured.'))
        
        api_url = 'https://loopjet-api.fly.dev'
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        }
        
        try:
            # 1. Sync all products/services (batch API)
            _logger.info("Syncing all products to Loopjet...")
            self._batch_sync_products(api_url, headers)
            
            # 2. Sync the customer contact
            _logger.info(f"Syncing customer {self.customer_id.name} to Loopjet...")
            self._sync_customer_contact(api_url, headers)
            
            # 3. Sync related invoices and estimates for context
            _logger.info("Syncing related invoices and estimates to Loopjet...")
            self._sync_related_documents(api_url, headers)
            
            _logger.info("All data synced successfully to Loopjet")
            
        except Exception as e:
            error_msg = f"Failed to sync data to Loopjet: {str(e)}"
            _logger.error(error_msg)
            raise UserError(_(f'Data Sync Error\n\n{error_msg}'))

    def _batch_sync_products(self, api_url, headers):
        """Batch sync all products to Loopjet."""
        products = self.env['product.template'].search([
            ('sale_ok', '=', True),  # Only products that can be sold
        ])
        
        if not products:
            _logger.info("No products found to sync")
            return
        
        product_list = []
        for product in products:
            product_list.append({
                'name': product.name,
                'description': product.description_sale or product.description or '',
                'is_service': product.type == 'service',
                'price': float(product.list_price),
                'currency': product.currency_id.name if product.currency_id else 'EUR',
                'unit': product.uom_id.name if product.uom_id else 'piece',
            })
        
        try:
            url = f"{api_url}/api/v1/batch/products/batch"
            response = requests.post(
                url, 
                json={'products': product_list, 'upsert': True}, 
                headers=headers, 
                timeout=60
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                success_count = result.get('created', 0) + result.get('updated', 0)
                _logger.info(f"Successfully synced {success_count} products to Loopjet")
            else:
                _logger.error(f"Batch product sync failed: {response.text}")
                raise Exception(f"Product sync failed: {response.text[:200]}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to connect to Loopjet API for product sync: {str(e)}")

    def _sync_customer_contact(self, api_url, headers):
        """Sync the customer contact to Loopjet."""
        if not self.customer_id:
            return
        
        contact_data = {
            'name': self.customer_id.name,
            'email': self.customer_id.email or None,
            'phone': self.customer_id.phone or None,
            'address_line1': self.customer_id.street or None,
            'address_line2': self.customer_id.street2 or None,
            'city': self.customer_id.city or None,
            'state': self.customer_id.state_id.name if self.customer_id.state_id else None,
            'postal_code': self.customer_id.zip or None,
            'country': self.customer_id.country_id.name if self.customer_id.country_id else None,
            'company': self.customer_id.commercial_company_name or self.customer_id.name,
            'tax_id': self.customer_id.vat or None,
            'website': self.customer_id.website or None,
            'notes': self.customer_id.comment or None,
            'type': 'customer',
        }
        
        # Remove None values
        contact_data = {k: v for k, v in contact_data.items() if v is not None}
        
        try:
            # Use batch endpoint with upsert to avoid duplicates
            url = f"{api_url}/api/v1/batch/contacts/batch"
            response = requests.post(
                url, 
                json={'contacts': [contact_data], 'upsert': True}, 
                headers=headers, 
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                _logger.info(f"Successfully synced contact {self.customer_id.name} to Loopjet")
            else:
                _logger.warning(f"Contact sync failed (non-critical): {response.text}")
        except Exception as e:
            _logger.warning(f"Failed to sync contact (non-critical): {str(e)}")

    def _sync_related_documents(self, api_url, headers):
        """Sync related invoices and estimates for this customer to provide context."""
        if not self.customer_id:
            return
        
        # Sync recent invoices for this customer (last 10)
        invoices = self.env['account.move'].search([
            ('partner_id', '=', self.customer_id.id),
            ('move_type', 'in', ['out_invoice', 'out_refund']),
            ('state', '!=', 'cancel'),
        ], limit=10, order='invoice_date desc')
        
        if invoices:
            invoice_list = []
            for invoice in invoices:
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
                
                invoice_list.append(invoice_data)
            
            try:
                url = f"{api_url}/api/v1/batch/invoices/batch"
                response = requests.post(url, json={'invoices': invoice_list}, headers=headers, timeout=60)
                
                if response.status_code in [200, 201]:
                    _logger.info(f"Successfully synced {len(invoice_list)} invoices to Loopjet")
                else:
                    _logger.warning(f"Invoice sync failed (non-critical): {response.text}")
            except Exception as e:
                _logger.warning(f"Failed to sync invoices (non-critical): {str(e)}")
        
        # Sync recent estimates/quotations for this customer (last 10)
        estimates = self.env['sale.order'].search([
            ('partner_id', '=', self.customer_id.id),
            ('state', 'in', ['draft', 'sent']),
        ], limit=10, order='date_order desc')
        
        if estimates:
            estimate_list = []
            for estimate in estimates:
                estimate_data = {
                    'estimate_number': estimate.name,
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
                        })
                
                estimate_list.append(estimate_data)
            
            try:
                url = f"{api_url}/api/v1/batch/estimates/batch"
                response = requests.post(url, json={'estimates': estimate_list}, headers=headers, timeout=60)
                
                if response.status_code in [200, 201]:
                    _logger.info(f"Successfully synced {len(estimate_list)} estimates to Loopjet")
                else:
                    _logger.warning(f"Estimate sync failed (non-critical): {response.text}")
            except Exception as e:
                _logger.warning(f"Failed to sync estimates (non-critical): {str(e)}")

