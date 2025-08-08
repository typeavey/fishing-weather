#!/bin/bash

# Production Status Script for Fishing Weather Portal

echo "📊 Fishing Weather Portal Status"
echo "================================"

# Check service status
echo "🔧 Service Status:"
sudo systemctl status fishing-weather --no-pager -l | head -10

# Check Apache status
echo ""
echo "🌐 Apache Status:"
sudo systemctl status httpd --no-pager -l | head -5

# Check SSL certificate
echo ""
echo "🔒 SSL Certificate:"
if [ -f "/etc/letsencrypt/live/fishing.thepeaveys.net/cert.pem" ]; then
    echo "✅ SSL certificate found"
    sudo openssl x509 -in /etc/letsencrypt/live/fishing.thepeaveys.net/cert.pem -noout -dates
else
    echo "❌ SSL certificate not found"
fi

# Test internal service
echo ""
echo "🧪 Internal Service Test:"
if curl -s http://localhost:5000/api/health > /dev/null; then
    echo "✅ Internal service is responding"
else
    echo "❌ Internal service is not responding"
fi

# Test production URL
echo ""
echo "🌐 Production URL Test:"
if curl -s -k https://fishing.thepeaveys.net/api/health > /dev/null; then
    echo "✅ Production portal is responding"
else
    echo "❌ Production portal is not responding"
fi

echo ""
echo "📋 Useful Commands:"
echo "   ./deploy-production.sh    # Deploy updates"
echo "   sudo systemctl restart fishing-weather  # Restart service"
echo "   ./backup-database.sh      # Backup database"
echo "   ./status.sh               # Check status"
