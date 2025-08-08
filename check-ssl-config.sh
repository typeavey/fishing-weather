#!/bin/bash

# Check and configure SSL setup for Fishing Weather Portal
# This script helps identify your existing SSL configuration

echo "🔒 Checking SSL configuration for fishing.thepeaveys.net..."

# Check if Apache is running
if ! sudo systemctl is-active --quiet httpd; then
    echo "❌ Apache is not running. Starting Apache..."
    sudo systemctl start httpd
fi

# Check for existing SSL certificates
echo "🔍 Checking for existing SSL certificates..."

# Common SSL certificate locations
SSL_PATHS=(
    "/etc/ssl/certs/fishing.thepeaveys.net.crt"
    "/etc/ssl/certs/fishing.thepeaveys.net.pem"
    "/etc/pki/tls/certs/fishing.thepeaveys.net.crt"
    "/etc/pki/tls/certs/fishing.thepeaveys.net.pem"
    "/etc/letsencrypt/live/fishing.thepeaveys.net/fullchain.pem"
    "/etc/letsencrypt/live/fishing.thepeaveys.net/cert.pem"
)

# Common SSL key locations
SSL_KEY_PATHS=(
    "/etc/ssl/private/fishing.thepeaveys.net.key"
    "/etc/ssl/private/fishing.thepeaveys.net.pem"
    "/etc/pki/tls/private/fishing.thepeaveys.net.key"
    "/etc/pki/tls/private/fishing.thepeaveys.net.pem"
    "/etc/letsencrypt/live/fishing.thepeaveys.net/privkey.pem"
)

# Common SSL chain locations
SSL_CHAIN_PATHS=(
    "/etc/ssl/certs/fishing.thepeaveys.net.chain.crt"
    "/etc/ssl/certs/fishing.thepeaveys.net.chain.pem"
    "/etc/pki/tls/certs/fishing.thepeaveys.net.chain.crt"
    "/etc/pki/tls/certs/fishing.thepeaveys.net.chain.pem"
    "/etc/letsencrypt/live/fishing.thepeaveys.net/chain.pem"
)

echo "📁 Checking for SSL certificates..."

# Find certificate
CERT_PATH=""
for path in "${SSL_PATHS[@]}"; do
    if [ -f "$path" ]; then
        CERT_PATH="$path"
        echo "✅ Found SSL certificate: $path"
        break
    fi
done

if [ -z "$CERT_PATH" ]; then
    echo "❌ No SSL certificate found in common locations"
    echo "💡 You may need to:"
    echo "   1. Install a certificate using Let's Encrypt:"
    echo "      sudo certbot --apache -d fishing.thepeaveys.net"
    echo "   2. Or place your certificate in one of these locations:"
    printf "      %s\n" "${SSL_PATHS[@]}"
fi

# Find private key
KEY_PATH=""
for path in "${SSL_KEY_PATHS[@]}"; do
    if [ -f "$path" ]; then
        KEY_PATH="$path"
        echo "✅ Found SSL private key: $path"
        break
    fi
done

if [ -z "$KEY_PATH" ]; then
    echo "❌ No SSL private key found in common locations"
    echo "💡 You may need to:"
    echo "   1. Install a certificate using Let's Encrypt:"
    echo "      sudo certbot --apache -d fishing.thepeaveys.net"
    echo "   2. Or place your private key in one of these locations:"
    printf "      %s\n" "${SSL_KEY_PATHS[@]}"
fi

# Find chain certificate
CHAIN_PATH=""
for path in "${SSL_CHAIN_PATHS[@]}"; do
    if [ -f "$path" ]; then
        CHAIN_PATH="$path"
        echo "✅ Found SSL chain certificate: $path"
        break
    fi
done

if [ -z "$CHAIN_PATH" ]; then
    echo "⚠️  No SSL chain certificate found (this may be optional)"
fi

# Check Apache SSL configuration
echo "🌐 Checking Apache SSL configuration..."

if [ -f "/etc/httpd/conf.d/fishing-weather.conf" ]; then
    echo "✅ Found fishing-weather.conf"
    
    # Check if SSL is configured
    if grep -q "SSLEngine on" /etc/httpd/conf.d/fishing-weather.conf; then
        echo "✅ SSL is configured in fishing-weather.conf"
    else
        echo "⚠️  SSL not configured in fishing-weather.conf"
    fi
else
    echo "❌ fishing-weather.conf not found"
fi

# Check if mod_ssl is enabled
if apache2ctl -M 2>/dev/null | grep -q ssl_module; then
    echo "✅ mod_ssl is enabled"
elif httpd -M 2>/dev/null | grep -q ssl_module; then
    echo "✅ mod_ssl is enabled"
else
    echo "⚠️  mod_ssl may not be enabled"
fi

# Test HTTPS connectivity
echo "🧪 Testing HTTPS connectivity..."
if curl -s -k https://fishing.thepeaveys.net > /dev/null 2>&1; then
    echo "✅ HTTPS is working for fishing.thepeaveys.net"
else
    echo "❌ HTTPS is not working for fishing.thepeaveys.net"
    echo "💡 This may be normal if the domain is not configured yet"
fi

# Check for Let's Encrypt
if [ -d "/etc/letsencrypt/live/fishing.thepeaveys.net" ]; then
    echo "✅ Let's Encrypt certificate found for fishing.thepeaveys.net"
    echo "📅 Certificate expires: $(openssl x509 -in /etc/letsencrypt/live/fishing.thepeaveys.net/cert.pem -noout -enddate 2>/dev/null | cut -d= -f2)"
fi

echo ""
echo "🔧 Next steps:"
echo ""

if [ -n "$CERT_PATH" ] && [ -n "$KEY_PATH" ]; then
    echo "✅ SSL certificates found! You can now:"
    echo "   1. Run the production setup: ./setup-production.sh"
    echo "   2. The script will use your existing SSL certificates"
else
    echo "❌ SSL certificates not found. You need to:"
    echo "   1. Install SSL certificates first:"
    echo "      sudo certbot --apache -d fishing.thepeaveys.net"
    echo "   2. Then run the production setup: ./setup-production.sh"
fi

echo ""
echo "📋 Manual SSL configuration:"
echo "   If your SSL certificates are in different locations,"
echo "   edit /etc/httpd/conf.d/fishing-weather.conf and update:"
echo "   - SSLCertificateFile"
echo "   - SSLCertificateKeyFile"
echo "   - SSLCertificateChainFile (if needed)"
