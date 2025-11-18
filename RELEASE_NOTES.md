# Release Notes

## Version 19.0.1.0.4 (November 2025)

### 🎉 Major Improvements

#### Automatic Data Synchronization
No more manual syncing! When you generate AI estimates, the plugin now automatically syncs:
- ✅ **All products/services** - Complete catalog available to AI
- ✅ **Customer contact** - Always up-to-date information  
- ✅ **Related invoices** - Last 10 for pricing context
- ✅ **Related estimates** - Last 10 for historical context

#### Simplified User Experience
- 🗑️ **Removed manual sync buttons** - No longer needed
- 🗑️ **Removed auto-sync toggles** - Always syncs automatically
- 🗑️ **Removed "Allow New Items" option** - AI now only uses your existing products
- ✨ **Cleaner settings page** - Less clutter, clearer purpose

#### Better Validation
- ✅ **Product validation** - Clear error if no products exist
- ✅ **Helpful guidance** - Step-by-step instructions when issues occur
- ✅ **Predictable behavior** - AI only uses your defined catalog

### ⚠️ Breaking Changes

**Important for existing users:**

1. **AI Behavior Changed**
   - **Before:** AI could create new items not in your catalog (if enabled)
   - **After:** AI ONLY uses existing products/services from your catalog
   - **Action Required:** Ensure you have products created before generating estimates

2. **Field Removed**
   - The `allow_new_items` field has been removed from the wizard
   - Upgrade will handle this automatically
   - No manual intervention needed

### 📋 What You Need to Do

**Before upgrading:**
1. Make sure you have products/services created in Odoo
2. Test with a sample CRM opportunity
3. Backup your database (recommended)

**After upgrading:**
1. Go to Settings > Loopjet Integration
2. Verify your API key is still configured
3. Create a test CRM opportunity
4. Click "Create Quotation with Loopjet"
5. Verify automatic sync works

**If you have no products:**
- Go to Sales → Products → Products
- Create your products/services
- Then try generating estimates

### 🚀 Benefits

- **Faster workflow** - No manual sync needed
- **Always current** - AI has latest data automatically
- **More predictable** - AI only uses your catalog
- **Better errors** - Clear guidance when something's wrong
- **Less confusion** - Fewer settings to manage

### 🔧 Technical Changes

- Moved sync logic from model hooks to wizard pre-generation
- Uses batch API endpoints for efficient syncing
- Non-critical syncs (contacts, invoices) fail gracefully
- Product sync is critical and shows error if it fails
- `allow_new_items` parameter hardcoded to `False`
- Pre-generation validation for product existence

### 🐛 Bug Fixes

- Fixed Python 3.12 compatibility in Docker setup
- Added `packaging` dependency for Odoo 19
- Improved error messages and user guidance

### 📚 Documentation Updates

- Updated INSTALLATION.md with new sync workflow
- Added comprehensive Docker setup (README.docker.md)
- Added Docker quickstart script
- Updated CHANGELOG.md with all changes

---

## Upgrade Instructions

### For Self-Hosted/On-Premise

```bash
# 1. Backup your database
pg_dump your_database > backup_before_1.0.4.sql

# 2. Update the module
cd /path/to/odoo/addons/loopjet_integration
git pull origin 19.0

# 3. Restart Odoo with upgrade
./odoo-bin -c odoo.conf -u loopjet_integration -d your_database

# 4. Test the new features
```

### For Odoo.sh (PaaS)

1. Push changes to your branch
2. Odoo.sh will automatically upgrade
3. Test in staging before production
4. Promote to production when ready

### For Docker

```bash
# 1. Pull latest changes
git pull origin 19.0

# 2. Rebuild and upgrade
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# 3. Upgrade module
make upgrade
```

---

## Support

Need help with the upgrade?

- 📧 Email: support@loopjet.io
- 📚 Documentation: https://docs.loopjet.io
- 🌐 Website: https://loopjet.io

## Feedback

We'd love to hear your thoughts on these changes! Please let us know:
- What you like about the new automatic sync
- Any issues you encounter
- Feature requests for future versions

Happy estimating! 🎉

