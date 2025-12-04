# -*- coding: utf-8 -*-
# Migration script for Loopjet Integration v19.0.1.0.5

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """
    Migration for version 19.0.1.0.5
    
    Changes:
    - Improved currency handling (uses company currency as fallback)
    - Improved unit handling (consistent 'unit' fallback)
    - Added currency to invoice and estimate line items when syncing
    - Replaced narrow alert with web_ribbon widget for AI-generated indicator
    
    Note: No database changes required for this version.
    """
    _logger.info("=" * 80)
    _logger.info("Migrating Loopjet Integration to version 19.0.1.0.5")
    _logger.info("=" * 80)
    
    _logger.info("Changes in this version:")
    _logger.info("  - Currency fallback: product → company → EUR")
    _logger.info("  - Unit fallback: product UoM → 'unit'")
    _logger.info("  - Currency added to synced invoice/estimate line items")
    _logger.info("  - UI: Replaced alert with web_ribbon widget")
    
    _logger.info("No database changes required for this version.")
    _logger.info("Migration to 19.0.1.0.5 completed successfully")
    _logger.info("=" * 80)

