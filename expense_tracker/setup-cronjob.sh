#!/bin/bash

PROJECT_DIR="/home/longhd/project/tinhtienHNAG/Bot-HNAG/expense_tracker" 

echo "📅 Setting up cronjob for auto-start..."

# Make scripts executable
chmod +x $PROJECT_DIR/start-services.sh
chmod +x $PROJECT_DIR/stop-services.sh

# Add to crontab
(crontab -l 2>/dev/null; echo "@reboot sleep 30 && $PROJECT_DIR/start-services.sh") | crontab -

echo "✅ Cronjob added! Services will auto-start 30 seconds after boot."
echo "📋 Current crontab:"
crontab -l