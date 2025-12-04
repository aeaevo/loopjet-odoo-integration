# -*- coding: utf-8 -*-
# Migration script for Loopjet Integration v18.0.1.0.4

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """
    Migration for version 18.0.1.0.4
    
    Changes:
    - Removed 'allow_new_items' field from wizard (now always False)
    - Added automatic data sync on estimate generation
    - Added product validation
    """
    _logger.info("=" * 80)
    _logger.info("Migrating Loopjet Integration to version 18.0.1.0.4")
    _logger.info("=" * 80)
    
    # Check if the wizard model exists and has records with the old field
    cr.execute("""
        SELECT COUNT(*) 
        FROM information_schema.columns 
        WHERE table_name='loopjet_generate_estimate_wizard' 
        AND column_name='allow_new_items'
    """)
    
    if cr.fetchone()[0] > 0:
        _logger.info("Found 'allow_new_items' field in wizard table")
        _logger.info("This field will be automatically removed by Odoo during module upgrade")
    
    _logger.info("Migration changes:")
    _logger.info("  - AI now ALWAYS uses existing products only")
    _logger.info("  - Automatic sync on estimate generation enabled")
    _logger.info("  - Product validation added before generation")
    
    _logger.info("Migration to 18.0.1.0.4 completed successfully")
    _logger.info("=" * 80)

