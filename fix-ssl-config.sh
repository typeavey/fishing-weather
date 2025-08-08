#!/bin/bash

# Fix SSL configuration for Fishing Weather Portal
# This script finds actual SSL certificates and updates Apache configuration

echo "🔧 Fixing SSL configuration for fishing.thepeaveys.net..."

# Step 1: Find existing SSL certificates
echo "🔍 Searching for existing SSL certificates..."

# Common SSL certificate locations
SSL_PATHS=(
    "/etc/ssl/certs/fishing.thepeaveys.net.crt"
    "/etc/ssl/certs/fishing.thepeaveys.net.pem"
    "/etc/pki/tls/certs/fishing.thepeaveys.net.crt"
    "/etc/pki/tls/certs/fishing.thepeaveys.net.pem"
    "/etc/letsencrypt/live/fishing.thepeaveys.net/fullchain.pem"
    "/etc/letsencrypt/live/fishing.thepeaveys.net/cert.pem"
    "/etc/ssl/certs/star.thepeaveys.net.crt"
    "/etc/ssl/certs/star.thepeaveys.net.pem"
    "/etc/pki/tls/certs/star.thepeaveys.net.crt"
    "/etc/pki/tls/certs/star.thepeaveys.net.pem"
)

# Common SSL key locations
SSL_KEY_PATHS=(
    "/etc/ssl/private/fishing.thepeaveys.net.key"
    "/etc/ssl/private/fishing.thepeaveys.net.pem"
    "/etc/pki/tls/private/fishing.thepeaveys.net.key"
    "/etc/pki/tls/private/fishing.thepeaveys.net.pem"
    "/etc/letsencrypt/live/fishing.thepeaveys.net/privkey.pem"
    "/etc/ssl/private/star.thepeaveys.net.key"
    "/etc/ssl/private/star.thepeaveys.net.pem"
    "/etc/pki/tls/private/star.thepeaveys.net.key"
    "/etc/pki/tls/private/star.thepeaveys.net.pem"
)

# Find certificate
CERT_PATH=""
for path in "${SSL_PATHS[@]}"; do
    if [ -f "$path" ]; then
        CERT_PATH="$path"
        echo "✅ Found SSL certificate: $path"
        break
    fi
done

# Find private key
KEY_PATH=""
for path in "${SSL_KEY_PATHS[@]}"; do
    if [ -f "$path" ]; then
        KEY_PATH="$path"
        echo "✅ Found SSL private key: $path"
        break
    fi
done

# Step 2: Check for wildcard certificates
if [ -z "$CERT_PATH" ]; then
    echo "🔍 Checking for wildcard certificates..."
    WILDCARD_CERTS=$(sudo find /etc -name "*thepeaveys.net*" -type f 2>/dev/null | grep -E "\.(crt|pem)$")
    if [ -n "$WILDCARD_CERTS" ]; then
        echo "📁 Found potential certificates:"
        echo "$WILDCARD_CERTS"
        CERT_PATH=$(echo "$WILDCARD_CERTS" | head -1)
        echo "✅ Using certificate: $CERT_PATH"
    fi
fi

# Step 3: Check for Let's Encrypt
if [ -z "$CERT_PATH" ] && [ -d "/etc/letsencrypt/live" ]; then
    echo "🔍 Checking Let's Encrypt certificates..."
    LE_DOMAINS=$(sudo find /etc/letsencrypt/live -maxdepth 1 -type d 2>/dev/null | grep -v "^/etc/letsencrypt/live$")
    if [ -n "$LE_DOMAINS" ]; then
        echo "📁 Found Let's Encrypt domains:"
        echo "$LE_DOMAINS"
        # Use the first domain found
        FIRST_DOMAIN=$(echo "$LE_DOMAINS" | head -1 | xargs basename)
        CERT_PATH="/etc/letsencrypt/live/$FIRST_DOMAIN/cert.pem"
        KEY_PATH="/etc/letsencrypt/live/$FIRST_DOMAIN/privkey.pem"
        echo "✅ Using Let's Encrypt certificate for: $FIRST_DOMAIN"
    fi
fi

# Step 4: If no certificates found, create a temporary configuration
if [ -z "$CERT_PATH" ]; then
    echo "⚠️  No SSL certificates found. Creating HTTP-only configuration..."
    
    # Create HTTP-only configuration
    sudo tee /etc/httpd/conf.d/fishing-weather.conf << EOF
# Fishing Weather Portal Production Configuration (HTTP Only)
<VirtualHost *:80>
    ServerName fishing.thepeaveys.net
    ServerAlias www.fishing.thepeaveys.net
    
    # Proxy all requests to internal Flask app
    ProxyPreserveHost On
    ProxyPass / http://localhost:5000/
    ProxyPassReverse / http://localhost:5000/
    
    # Security headers
    Header always set X-Content-Type-Options nosniff
    Header always set X-Frame-Options DENY
    Header always set X-XSS-Protection "1; mode=block"
    
    # Logging
    ErrorLog /var/log/httpd/fishing-weather-error.log
    CustomLog /var/log/httpd/fishing-weather-access.log combined
</VirtualHost>
EOF

    echo "✅ Created HTTP-only configuration"
    echo "💡 To add SSL later, run: sudo certbot --apache -d fishing.thepeaveys.net"
    
else
    echo "✅ Found SSL certificates. Creating HTTPS configuration..."
    
    # Create HTTPS configuration with found certificates
    sudo tee /etc/httpd/conf.d/fishing-weather.conf << EOF
# Fishing Weather Portal Production Configuration with SSL Support

# HTTP Virtual Host (redirect to HTTPS)
<VirtualHost *:80>
    ServerName fishing.thepeaveys.net
    ServerAlias www.fishing.thepeaveys.net
    
    # Redirect all HTTP traffic to HTTPS
    Redirect permanent / https://fishing.thepeaveys.net/
    
    # Logging
    ErrorLog /var/log/httpd/fishing-weather-error.log
    CustomLog /var/log/httpd/fishing-weather-access.log combined
</VirtualHost>

# HTTPS Virtual Host
<VirtualHost *:443>
    ServerName fishing.thepeaveys.net
    ServerAlias www.fishing.thepeaveys.net
    
    # SSL Configuration
    SSLEngine on
    SSLCertificateFile $CERT_PATH
    SSLCertificateKeyFile $KEY_PATH
EOF

    # Add chain certificate if it exists
    if [ -f "${CERT_PATH%.*}.chain.${CERT_PATH##*.}" ]; then
        echo "    SSLCertificateChainFile ${CERT_PATH%.*}.chain.${CERT_PATH##*.}" >> /etc/httpd/conf.d/fishing-weather.conf
    elif [ -f "${CERT_PATH%.*}.chain.crt" ]; then
        echo "    SSLCertificateChainFile ${CERT_PATH%.*}.chain.crt" >> /etc/httpd/conf.d/fishing-weather.conf
    fi
    
    # Complete the configuration
    cat >> /etc/httpd/conf.d/fishing-weather.conf << EOF
    
    # Security headers
    Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
    Header always set X-Content-Type-Options nosniff
    Header always set X-Frame-Options DENY
    Header always set X-XSS-Protection "1; mode=block"
    Header always set Referrer-Policy "strict-origin-when-cross-origin"
    
    # Proxy all requests to internal Flask app
    ProxyPreserveHost On
    ProxyPass / http://localhost:5000/
    ProxyPassReverse / http://localhost:5000/
    
    # Logging
    ErrorLog /var/log/httpd/fishing-weather-ssl-error.log
    CustomLog /var/log/httpd/fishing-weather-ssl-access.log combined
</VirtualHost>
EOF

    echo "✅ Created HTTPS configuration with certificates:"
    echo "   Certificate: $CERT_PATH"
    echo "   Private Key: $KEY_PATH"
fi

# Step 5: Enable required Apache modules
echo "🔧 Enabling Apache modules..."
sudo dnf install -y mod_ssl 2>/dev/null || true

# Step 6: Test Apache configuration
echo "🧪 Testing Apache configuration..."
if sudo apachectl configtest; then
    echo "✅ Apache configuration is valid"
else
    echo "❌ Apache configuration has errors"
    echo "📋 Checking Apache error log..."
    sudo tail -5 /var/log/httpd/error_log 2>/dev/null || echo "No error log found"
    exit 1
fi

# Step 7: Restart Apache
echo "🔄 Restarting Apache..."
sudo systemctl restart httpd

# Step 8: Check Apache status
echo "📊 Checking Apache status..."
sleep 3
if sudo systemctl is-active --quiet httpd; then
    echo "✅ Apache service is running!"
else
    echo "❌ Apache service failed to start"
    sudo systemctl status httpd --no-pager -l
    exit 1
fi

# Step 9: Test the application
echo "🧪 Testing application..."
sleep 3
if curl -s http://localhost:5000/api/health > /dev/null; then
    echo "✅ Internal Flask app is responding"
else
    echo "⚠️  Internal Flask app may not be ready"
fi

if [ -n "$CERT_PATH" ]; then
    if curl -s -k https://fishing.thepeaveys.net/api/health > /dev/null; then
        echo "✅ Production portal is responding via HTTPS"
    else
        echo "⚠️  Production portal may not be ready yet"
    fi
else
    if curl -s http://fishing.thepeaveys.net/api/health > /dev/null; then
        echo "✅ Production portal is responding via HTTP"
    else
        echo "⚠️  Production portal may not be ready yet"
    fi
fi

echo ""
echo "🎉 SSL configuration fix complete!"
echo ""
if [ -n "$CERT_PATH" ]; then
    echo "🌐 Your portal is available at:"
    echo "   https://fishing.thepeaveys.net"
    echo "   https://www.fishing.thepeaveys.net"
else
    echo "🌐 Your portal is available at:"
    echo "   http://fishing.thepeaveys.net"
    echo "   http://www.fishing.thepeaveys.net"
    echo ""
    echo "💡 To add SSL later:"
    echo "   sudo certbot --apache -d fishing.thepeaveys.net"
fi
