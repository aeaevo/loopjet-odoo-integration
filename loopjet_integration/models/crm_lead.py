# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    loopjet_estimate_count = fields.Integer(
        string='Loopjet Estimates',
        compute='_compute_loopjet_estimate_count',
        help='Number of estimates generated via Loopjet for this opportunity'
    )

    def _compute_loopjet_estimate_count(self):
        """Count sale orders created via Loopjet for this lead."""
        for lead in self:
            # In Odoo 19, the relationship might use different field names
            # Try to find sale orders linked to this opportunity
            domain = [('loopjet_generated', '=', True)]
            
            # Check which field name is used to link to opportunities
            SaleOrder = self.env['sale.order']
            if 'opportunity_id' in SaleOrder._fields:
                domain.append(('opportunity_id', '=', lead.id))
            elif 'crm_lead_id' in SaleOrder._fields:
                domain.append(('crm_lead_id', '=', lead.id))
            else:
                # Fallback: search in all Loopjet-generated orders for this partner
                if lead.partner_id:
                    domain.append(('partner_id', '=', lead.partner_id.id))
                else:
                    lead.loopjet_estimate_count = 0
                    continue
            
            lead.loopjet_estimate_count = SaleOrder.search_count(domain)

    def action_generate_loopjet_estimate(self):
        """Open wizard to generate estimate with Loopjet AI."""
        self.ensure_one()
        
        # Check if API key is configured
        api_key = self.env['ir.config_parameter'].sudo().get_param('loopjet.api_key')
        if not api_key:
            raise UserError(_(
                'Loopjet API key not configured.\n\n'
                'Please configure your Loopjet API key in:\n'
                'Settings > General Settings > Loopjet Integration'
            ))
        
        return {
            'name': _('Generate Estimate with Loopjet'),
            'type': 'ir.actions.act_window',
            'res_model': 'loopjet.generate.estimate.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_lead_id': self.id,
            }
        }
    
    def action_view_loopjet_estimates(self):
        """View all estimates generated via Loopjet for this lead."""
        self.ensure_one()
        
        action = self.env.ref('sale.action_quotations').read()[0]
        
        # Build domain based on available fields
        SaleOrder = self.env['sale.order']
        domain = [('loopjet_generated', '=', True)]
        
        if 'opportunity_id' in SaleOrder._fields:
            domain.append(('opportunity_id', '=', self.id))
            action['context'] = {'default_opportunity_id': self.id}
        elif 'crm_lead_id' in SaleOrder._fields:
            domain.append(('crm_lead_id', '=', self.id))
            action['context'] = {'default_crm_lead_id': self.id}
        elif self.partner_id:
            domain.append(('partner_id', '=', self.partner_id.id))
            action['context'] = {'default_partner_id': self.partner_id.id}
        
        action['domain'] = domain
        return action
    
    def extract_deal_information(self):
        """
        Extract comprehensive information from the CRM deal.
        
        Returns a formatted text suitable for AI processing, including:
        - Deal description and notes
        - Activities and logs
        - Messages and comments
        - Customer information
        - Expected revenue and probability
        """
        self.ensure_one()
        
        info_parts = []
        
        # Basic deal information
        info_parts.append(f"Deal: {self.name}")
        if self.partner_id:
            info_parts.append(f"Customer: {self.partner_id.name}")
            if self.partner_id.email:
                info_parts.append(f"Email: {self.partner_id.email}")
            if self.partner_id.phone:
                info_parts.append(f"Phone: {self.partner_id.phone}")
        
        # Expected revenue and stage
        if self.expected_revenue:
            info_parts.append(f"Expected Revenue: {self.expected_revenue} {self.company_currency.symbol if self.company_currency else ''}")
        if self.probability:
            info_parts.append(f"Probability: {self.probability}%")
        if self.stage_id:
            info_parts.append(f"Stage: {self.stage_id.name}")
        
        # Description/notes
        if self.description:
            info_parts.append(f"\nDescription:\n{self.description}")
        
        # Extract activities
        activities = self.env['mail.activity'].search([
            ('res_id', '=', self.id),
            ('res_model', '=', 'crm.lead'),
        ], order='date_deadline desc', limit=20)
        
        if activities:
            info_parts.append("\nActivities:")
            for activity in activities:
                activity_text = f"- [{activity.activity_type_id.name}] {activity.summary or ''}"
                if activity.note:
                    activity_text += f": {activity.note}"
                info_parts.append(activity_text)
        
        # Extract messages and comments
        messages = self.env['mail.message'].search([
            ('model', '=', 'crm.lead'),
            ('res_id', '=', self.id),
            ('message_type', 'in', ['comment', 'email']),
        ], order='date desc', limit=20)
        
        if messages:
            info_parts.append("\nConversation History:")
            for message in messages:
                if message.body:
                    # Clean HTML tags from body
                    from markupsafe import Markup
                    clean_body = Markup(message.body).striptags()
                    if clean_body.strip():
                        info_parts.append(f"- [{message.date}] {clean_body[:500]}")
        
        # Extract logged notes
        notes = self.env['mail.message'].search([
            ('model', '=', 'crm.lead'),
            ('res_id', '=', self.id),
            ('message_type', '=', 'notification'),
        ], order='date desc', limit=10)
        
        if notes:
            info_parts.append("\nInternal Notes:")
            for note in notes:
                if note.body:
                    from markupsafe import Markup
                    clean_body = Markup(note.body).striptags()
                    if clean_body.strip():
                        info_parts.append(f"- {clean_body[:300]}")
        
        # Tags
        if self.tag_ids:
            tags_text = ", ".join(self.tag_ids.mapped('name'))
            info_parts.append(f"\nTags: {tags_text}")
        
        return "\n".join(info_parts)

