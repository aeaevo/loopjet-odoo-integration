# Loopjet Odoo Integration - Development Dockerfile
FROM odoo:17

# Switch to root to install dependencies
USER root

# Install Python dependencies for the plugin
# Using --break-system-packages is safe in Docker containers (isolated environment)
# Install packaging first (needed by Odoo to parse version requirements)
RUN pip3 install --no-cache-dir --break-system-packages packaging

# Install plugin dependencies
COPY loopjet_integration/requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir --break-system-packages -r /tmp/requirements.txt

# Create directory for extra addons
RUN mkdir -p /mnt/extra-addons

# Copy the plugin to extra-addons directory
COPY loopjet_integration /mnt/extra-addons/loopjet_integration

# Set proper permissions
RUN chown -R odoo:odoo /mnt/extra-addons

# Switch back to odoo user
USER odoo

# The base odoo image already has the correct entrypoint and cmd
# ENTRYPOINT ["/entrypoint.sh"]
# CMD ["odoo"]

