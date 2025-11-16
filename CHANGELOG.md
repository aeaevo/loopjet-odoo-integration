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

