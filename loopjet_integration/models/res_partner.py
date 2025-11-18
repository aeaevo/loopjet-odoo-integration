# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests
import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    loopjet_contact_id = fields.Char(
        string='Loopjet Contact ID',
        readonly=True,
        help='UUID of this contact in Loopjet system'
    )
    
    loopjet_synced = fields.Boolean(
        string='Synced to Loopjet',
        default=False,
        readonly=True,
        help='Whether this contact has been synchronized to Loopjet'
    )
    
    loopjet_last_sync = fields.Datetime(
        string='Last Loopjet Sync',
        readonly=True,
        help='Last time this contact was synced to Loopjet'
    )

    def sync_to_loopjet(self):
        """Sync this contact to Loopjet."""
        for contact in self:
            try:
                # Get API configuration
                api_key = self.env['ir.config_parameter'].sudo().get_param('loopjet.api_key')
                if not api_key:
                    _logger.warning('Loopjet API key not configured, skipping contact sync')
                    return
                
                api_url = 'https://loopjet-api.fly.dev'
                headers = {
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json',
                }
                
                # Prepare contact data
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
                
                # If already synced, update; otherwise create
                if contact.loopjet_contact_id:
                    # Update existing contact
                    url = f"{api_url}/api/v1/contacts/{contact.loopjet_contact_id}"
                    response = requests.put(url, json=contact_data, headers=headers, timeout=30)
                else:
                    # Create new contact
                    url = f"{api_url}/api/v1/contacts/"
                    response = requests.post(url, json=contact_data, headers=headers, timeout=30)
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    contact.write({
                        'loopjet_contact_id': result.get('id'),
                        'loopjet_synced': True,
                        'loopjet_last_sync': fields.Datetime.now(),
                    })
                    _logger.info(f"Successfully synced contact {contact.name} to Loopjet")
                else:
                    _logger.error(f"Failed to sync contact {contact.name}: {response.text}")
                    
            except Exception as e:
                _logger.error(f"Error syncing contact {contact.name} to Loopjet: {str(e)}")


