# Changelog

All notable changes to the Loopjet Odoo Integration will be documented in this file.

## [1.0.0] - 2025-11-15

### Added
- Initial release of Loopjet Odoo Integration
- One-click AI estimate generation from CRM opportunities
- Automatic extraction of deal information (notes, logs, comments, activities)
- AI-powered estimate item suggestions via Loopjet API
- Seamless creation of prefilled quotations/sale orders
- Product synchronization with Loopjet
- Multi-language support (English, German, Spanish, French)
- Configuration panel in Odoo settings
- Smart button to view Loopjet-generated estimates
- Loopjet metadata tab in sale orders
- Support for custom instructions during estimate generation
- Toggle to allow/disallow new product creation by AI
- Comprehensive error handling and user feedback
- Credit balance checking before API calls

### Features
- CRM integration with "Create Estimate with Loopjet" button
- Deal information extraction from:
  - Basic deal data (name, customer, revenue, probability)
  - Description and notes
  - Activities (calls, meetings, to-dos)
  - Conversation history (emails, comments)
  - Internal notes
  - Tags
- AI estimate generation with:
  - Intelligent product matching
  - Quantity suggestions
  - Pricing from catalog or AI recommendations
  - Discount suggestions
  - Tax calculations
- Product synchronization:
  - Manual sync via product action menu
  - Optional auto-sync on create/update
- Sale order enhancements:
  - Loopjet generation indicator
  - AI reasoning display
  - Raw API response storage (for admins)
  - Filter for AI-generated quotes

### Technical
- Compatible with Odoo 14.0+
- Python dependencies: requests>=2.28.0
- RESTful API integration with Loopjet
- JWT authentication support
- Error handling with user-friendly messages
- Logging for debugging and monitoring

### Documentation
- Comprehensive README with features and usage
- Detailed installation guide
- HTML description for Odoo Apps
- Requirements file for dependencies

### Security
- API key stored in Odoo system parameters
- Password field for API key input
- Access rights for sales users and managers

## [1.0.4] - 2025-11-18

### Changed
- **Automatic Data Synchronization**: When generating AI estimates, the plugin now automatically syncs:
  - All products/services to provide complete catalog to AI
  - Customer contact information
  - Related invoices and estimates (last 10) for historical context
- Removed manual sync buttons from settings (no longer needed)
- Removed auto-sync toggle settings (always syncs on estimate generation)
- Simplified settings page with clear explanation of automatic sync behavior
- Updated INSTALLATION.md to reflect new sync workflow
- **Removed "Allow AI to Generate New Items" checkbox**: AI now ALWAYS uses existing products/services only
- **Added product validation**: Shows clear error if no products exist, guiding users to create products first

### Added
- Docker support with complete setup (Dockerfile, docker-compose.yml)
- Makefile for convenient Docker commands
- Migration script for smooth upgrades
- RELEASE_NOTES.md with detailed upgrade instructions
- README.docker.md with comprehensive Docker documentation
- DOCKER_OVERVIEW.md with visual guides and workflows

### Fixed
- Python 3.12 compatibility in Docker (PEP 668 handling)
- Added `packaging` dependency for Odoo 19 requirement parsing

### Benefits
- **Simpler UX**: No need to remember to sync data manually
- **Always Up-to-Date**: AI always has latest product catalog and customer data
- **Better Context**: AI receives historical invoices/estimates for better suggestions
- **Less Configuration**: Fewer settings to manage
- **More Predictable**: AI only uses your defined product catalog, no unexpected items
- **Better Guidance**: Clear error messages guide users when products are missing

### Technical
- Moved sync logic from model hooks to wizard pre-generation step
- Uses batch API endpoints for efficient syncing
- Non-critical syncs (contacts, invoices) fail gracefully without blocking AI generation
- Product sync is critical and will show error if fails
- `allow_new_items` parameter hardcoded to `False` in API calls
- Pre-generation validation checks for product existence

## [Unreleased]

### Planned
- Batch estimate generation for multiple deals
- Estimate templates
- Custom field mapping
- Webhook support for real-time sync
- Advanced product matching rules
- Estimate approval workflow
- Analytics and reporting dashboard
- Multi-currency support enhancements
- Custom discount rules integration
- PDF generation with Loopjet templates

