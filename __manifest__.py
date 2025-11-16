{
    'name': 'Loopjet AI Estimate Integration',
    'version': '19.0.1.0.3',
    'category': 'Sales',
    'summary': 'Generate AI-powered estimates from CRM deals using Loopjet',
    'description': """
        Loopjet AI Estimate Integration
        ================================
        
        This module integrates Loopjet's AI-powered estimate generation with Odoo CRM.
        
        Features:
        - One-click estimate generation from CRM opportunities/deals
        - Automatic extraction of deal information (notes, logs, comments, activities)
        - AI-powered estimate item suggestions
        - Seamless prefilling of Odoo sale orders/quotes
        - Product/service synchronization with Loopjet
        - Full Odoo 19 compatibility with latest UX improvements
        
        Requirements:
        - Odoo 14.0 or higher (tested with 14, 15, 16, 17, 18, and 19)
        - Active Loopjet account with API access
        - Loopjet API key configured in settings
    """,
    'author': 'Loopjet',
    'website': 'https://loopjet.io',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'crm',
        'sale',
        'product',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/crm_lead_views.xml',
        'views/sale_order_views.xml',
        'wizard/loopjet_generate_estimate_wizard.xml',
    ],
    'images': [
        'static/description/icon.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

