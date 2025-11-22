{
    'name': 'Loopjet AI Estimate Integration',
    'version': '18.0.1.0.5',
    'category': 'Sales',
    'summary': 'AI-Powered Estimate Generation from CRM Deals - Transform opportunities into quotes instantly',
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
        - Full Odoo 18 compatibility with latest UX improvements
        
        Requirements:
        - Odoo 18.0 (tested and verified for Odoo 18)
        - Active Loopjet account with API access
        - Loopjet API key configured in settings
        
        Compatibility:
        - ✅ Odoo.sh (PaaS)
        - ✅ On-premise / Self-hosted
        - ❌ Odoo Online (SaaS) - Not supported due to Python code restrictions
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
    'external_dependencies': {
        'python': ['requests', 'packaging'],
    },
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/crm_lead_views.xml',
        'views/sale_order_views.xml',
        'wizard/loopjet_generate_estimate_wizard.xml',
    ],
    'images': [
        'static/description/images/cover.png',
        'static/description/images/settings.png',
        'static/description/images/deal_overview.png',
        'static/description/images/loopjet_modal.png',
        'static/description/images/final_estimate.png',
        'static/description/images/main_screenshot.png',
        'static/description/icon.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

