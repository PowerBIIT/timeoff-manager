#!/bin/bash
# Setup SMTP configuration in Azure Web App

echo "📧 Konfigurowanie SMTP w Azure..."

# Upload setup script to Azure
az webapp deploy \
  --resource-group timeoff-rg-prod \
  --name timeoff-manager-20251004 \
  --src-path setup_smtp.py \
  --type static \
  --target-path setup_smtp.py

# Run the setup script via SSH
az webapp ssh \
  --resource-group timeoff-rg-prod \
  --name timeoff-manager-20251004 \
  --command "cd /home/site/wwwroot && python setup_smtp.py"

echo "✅ SMTP configuration completed!"
