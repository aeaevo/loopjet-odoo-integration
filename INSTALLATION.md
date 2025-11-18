# Loopjet Odoo Plugin - Installation Guide

## Prerequisites

- Odoo 19
- Access to Odoo server filesystem
- Odoo restart permissions
- Active Loopjet account (sign up at https://loopjet.io)

> **Note**: This module is fully tested and compatible with [Odoo 19](https://www.odoo.com/odoo-19-release-notes) (released September 2025) and benefits from the latest CRM and UI improvements.

## Installation Steps

### 1. Copy Module to Addons Directory

```bash
# Navigate to your Odoo addons directory
cd /path/to/odoo/addons

# Copy the odoo-plugin folder
cp -r /path/to/loopjet/apps/odoo-plugin ./loopjet_integration
```

Or create a symbolic link:

```bash
ln -s /path/to/loopjet/apps/odoo-plugin /path/to/odoo/addons/loopjet_integration
```

### 2. Install Python Dependencies

```bash
pip3 install -r /path/to/odoo/addons/loopjet_integration/requirements.txt
```

### 3. Update Odoo Addons Path (if needed)

If you placed the module in a custom addons directory, update your Odoo configuration file:

```ini
# /etc/odoo/odoo.conf
[options]
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/path/to/custom/addons,/path/to/loopjet_integration
```

### 4. Restart Odoo Server

```bash
# For system service
sudo systemctl restart odoo

# Or if running manually
./odoo-bin -c /etc/odoo/odoo.conf --stop-after-init
./odoo-bin -c /etc/odoo/odoo.conf
```

### 5. Update Apps List in Odoo

1. Login to Odoo as Administrator
2. Go to **Apps** menu
3. Click **Update Apps List** (⋮ menu → Update Apps List)
4. Search for "Loopjet"
5. Click **Install**

### 6. Configure Loopjet API Key

After installation:

1. Go to **Settings** → **General Settings**
2. Scroll to **Loopjet Integration** section
3. Enter your **Loopjet API Key**
   - Get your API key from: https://app.loopjet.io/api-usage
4. Configure optional settings:
   - **Default Language**: Choose language for AI-generated estimates
5. Click **Save**

> **Note**: Data synchronization happens automatically when you generate AI estimates. No manual syncing required!

## Verification

### Test the Installation

1. Go to **CRM** → **Pipeline**
2. Open any opportunity (or create a test one)
3. Look for the **"Create Quotation with Loopjet"** button in the header
4. Click it to open the estimate generation wizard
5. If you see the wizard with extracted deal information, installation is successful!

### Test API Connection

1. Create a test opportunity with:
   - Customer name
   - Description of services needed
   - Some notes or activities
2. Click **"Create Quotation with Loopjet"**
3. Click **"Generate Quotation"**
4. If it successfully generates an estimate, your API connection is working!

## Troubleshooting

### Module Not Appearing in Apps List

**Solution**:
```bash
# Restart Odoo with update
./odoo-bin -c /etc/odoo/odoo.conf -u all -d your_database --stop-after-init
```

### "Module not found" Error

**Solution**:
- Check addons_path in odoo.conf includes the module directory
- Verify file permissions (should be readable by Odoo user)
- Restart Odoo server

### "requests module not found" Error

**Solution**:
```bash
pip3 install requests
# Or
pip3 install -r requirements.txt
```

### API Key Not Saving

**Solution**:
- Make sure you're logged in as Administrator
- Check Settings → Technical → Parameters → System Parameters
- Look for `loopjet.api_key` parameter
- If missing, create it manually

### Button Not Showing in CRM

**Solution**:
- Clear browser cache
- Restart Odoo server
- Check module is installed (not just "To Install")
- Verify CRM app is installed

## Upgrading

To upgrade the module:

```bash
# Pull latest changes
cd /path/to/loopjet/apps/odoo-plugin
git pull

# Restart Odoo with upgrade flag
./odoo-bin -c /etc/odoo/odoo.conf -u loopjet_integration -d your_database
```

## Uninstallation

To uninstall the module:

1. Go to **Apps** in Odoo
2. Search for "Loopjet"
3. Click **Uninstall**
4. Confirm uninstallation

**Note**: This will remove:
- Loopjet configuration settings
- Custom fields added to CRM and Sale models
- Generated estimates will remain but lose Loopjet metadata

## Support

If you encounter issues:

1. Check Odoo server logs: `/var/log/odoo/odoo-server.log`
2. Check Loopjet API status: https://status.loopjet.io
3. Contact support:
   - Email: support@loopjet.io
   - Documentation: https://docs.loopjet.io
   - Website: https://loopjet.io

## Docker Installation

For Docker-based Odoo deployments:

```dockerfile
# Dockerfile
FROM odoo:17

# Install dependencies
USER root
RUN pip3 install requests

# Copy module
COPY ./odoo-plugin /mnt/extra-addons/loopjet_integration

USER odoo
```

```yaml
# docker-compose.yml
version: '3.1'
services:
  odoo:
    image: your-custom-odoo:17
    volumes:
      - ./odoo-plugin:/mnt/extra-addons/loopjet_integration
    environment:
      - ADDONS_PATH=/mnt/extra-addons
```

## Next Steps

After installation:

1. **Configure API Key** (required)
2. **Test with Sample Deal** to familiarize yourself
   - Create a CRM opportunity with a customer
   - Add description of services/products needed
   - Click "Create Quotation with Loopjet" 
   - Data syncs automatically before AI generation!
3. **Train Your Team** on how to use the feature
4. **Purchase Credits** if needed at https://app.loopjet.io/subscription

Happy estimating! 🎉

