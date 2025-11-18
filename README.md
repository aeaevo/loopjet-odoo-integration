# Loopjet AI Estimate Integration for Odoo

Generate AI-powered estimates from CRM opportunities/deals using Loopjet's advanced AI technology.

## Features

- **One-Click AI Estimate Generation**: Click a button in any CRM deal to generate a comprehensive estimate
- **Automatic Deal Information Extraction**: Extracts notes, logs, comments, activities, and conversation history
- **Intelligent Product Matching**: AI matches requirements to your product catalog or creates new items
- **Seamless Odoo Integration**: Creates prefilled quotations/sale orders directly in Odoo
- **Product Synchronization**: Optionally sync your Odoo products to Loopjet
- **Multi-language Support**: Generate estimates in English, German, Spanish, or French

## Requirements

- Odoo 19.0 or higher
- Active Loopjet account with API access
- Python packages: `requests`

### Odoo 19 Compatibility

This module is **fully compatible** with Odoo 19 (released September 2025) and takes advantage of new features like improved activities, enhanced CRM workflows, and better mobile support. See the [Odoo 19 Release Notes](https://www.odoo.com/odoo-19-release-notes) for details.

## Quick Start with Docker 🐳

The **fastest way** to test this plugin locally:

```bash
# Start Odoo with the plugin
docker-compose up -d

# Access Odoo at http://localhost:8069
# Follow the setup wizard to create a database
# Then install the Loopjet Integration from the Apps menu
```

**Full Docker documentation**: See [README.docker.md](README.docker.md) for detailed instructions, development mode, troubleshooting, and more.

**Quick commands**:
```bash
make up          # Start services
make logs        # View logs
make upgrade     # Upgrade the module
make clean       # Clean everything and start fresh
```

## Installation

### 1. Install the Module

Copy the `odoo-plugin` folder to your Odoo addons directory:

```bash
cp -r odoo-plugin /path/to/odoo/addons/loopjet_integration
```

### 2. Update Apps List

In Odoo, go to:
- **Apps** → **Update Apps List**
- Search for "Loopjet"
- Click **Install**

### 3. Configure API Key

After installation, configure your Loopjet API key:

1. Go to **Settings** → **General Settings**
2. Scroll to **Loopjet Integration** section
3. Enter your **Loopjet API Key** (get it from https://app.loopjet.io/settings)
4. (Optional) Configure other settings:
   - **API URL**: Default is `https://api.loopjet.io`
   - **Auto-sync Products**: Enable to automatically sync products to Loopjet
   - **Default Language**: Choose default language for AI estimates
5. Click **Save**

## Usage

### Generate AI Estimate from CRM Deal

1. Open a CRM **Opportunity** (Pipeline view or form)
2. Click the **"Create Estimate with Loopjet"** button (purple button with magic wand icon)
3. Review the extracted deal information
4. (Optional) Add additional instructions for the AI
5. Click **"Generate Estimate"**
6. Wait a few seconds while AI processes the request
7. Review the generated estimate preview
8. A new **Quotation** will be created and opened automatically

### Extracted Information

The AI analyzes the following from your CRM deal:

- **Deal name and description**
- **Customer information** (name, email, phone, address)
- **Expected revenue and probability**
- **Stage and status**
- **Activities** (calls, meetings, to-dos)
- **Conversation history** (emails, comments)
- **Internal notes**
- **Tags**

### Generated Estimate

The AI generates:

- **Line items** with products/services
- **Quantities** based on deal context
- **Pricing** from your product catalog or AI suggestions
- **Descriptions** tailored to customer needs
- **Reasoning** explaining the AI's decisions

## Configuration Options

### Settings → Loopjet Integration

| Setting | Description | Default |
|---------|-------------|---------|
| **API Key** | Your Loopjet authentication key (required) | - |
| **API URL** | Loopjet API endpoint | `https://api.loopjet.io` |
| **Auto-sync Products** | Automatically sync products to Loopjet | Disabled |
| **Default Language** | Language for AI-generated content | English |

### Product Synchronization

To sync products to Loopjet:

1. Go to **Sales** → **Products** → **Products**
2. Open a product
3. Click **Action** → **Sync to Loopjet**

Or enable **Auto-sync Products** in settings to sync automatically.

## Credits & Pricing

Generating estimates consumes Loopjet credits:

- **Simple estimate** (≤5 items, short description): **50 credits**
- **Medium estimate** (6-10 items): **75 credits**
- **Complex estimate** (>10 items or detailed): **100 credits**

Purchase credits in your Loopjet account at https://app.loopjet.io/subscription

## Troubleshooting

### "API key not configured" Error

**Solution**: Go to Settings → General Settings → Loopjet Integration and enter your API key.

### "Insufficient credits" Error

**Solution**: Purchase more credits in your Loopjet account.

### "Failed to connect to Loopjet API" Error

**Possible causes**:
- Check internet connectivity
- Verify API URL is correct
- Check firewall/proxy settings

### Products not syncing

**Solution**: 
- Check API key is valid
- Enable "Auto-sync Products" in settings
- Manually sync via product Action menu

## Support

- **Loopjet Website**: https://loopjet.io
- **Documentation**: https://docs.loopjet.io
- **Support Email**: support@loopjet.io
- **API Documentation**: https://loopjet.io/api-docs

## License

LGPL-3

## Credits

Developed by Loopjet Team
Website: https://loopjet.io

