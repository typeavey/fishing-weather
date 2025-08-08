# 🔒 SSL/HTTPS Setup Guide

## 🎯 **Your Rocky Server SSL Configuration**

Your Rocky server is already configured with SSL and can receive HTTPS traffic. This guide helps you integrate the fishing weather portal with your existing SSL setup.

## 🔍 **Step 1: Check Your Existing SSL Configuration**

Run the SSL check script to see what's already configured:

```bash
cd /home/typeavey/fishing-weather
./check-ssl-config.sh
```

This will:
- ✅ Check for existing SSL certificates
- ✅ Verify Apache SSL configuration
- ✅ Test HTTPS connectivity
- ✅ Provide next steps

## 🚀 **Step 2: Deploy with SSL Support**

If SSL certificates are found, deploy the portal:

```bash
./setup-production.sh
```

This will:
- ✅ Configure Apache virtual hosts for both HTTP and HTTPS
- ✅ Set up automatic HTTP to HTTPS redirects
- ✅ Configure security headers
- ✅ Use your existing SSL certificates

## 🔧 **SSL Certificate Locations**

The setup script looks for SSL certificates in these common locations:

### **Let's Encrypt (Most Common)**
```
Certificate: /etc/letsencrypt/live/fishing.thepeaveys.net/cert.pem
Private Key: /etc/letsencrypt/live/fishing.thepeaveys.net/privkey.pem
Chain: /etc/letsencrypt/live/fishing.thepeaveys.net/chain.pem
```

### **Traditional SSL**
```
Certificate: /etc/ssl/certs/fishing.thepeaveys.net.crt
Private Key: /etc/ssl/private/fishing.thepeaveys.net.key
Chain: /etc/ssl/certs/fishing.thepeaveys.net.chain.crt
```

### **System SSL**
```
Certificate: /etc/pki/tls/certs/fishing.thepeaveys.net.crt
Private Key: /etc/pki/tls/private/fishing.thepeaveys.net.key
Chain: /etc/pki/tls/certs/fishing.thepeaveys.net.chain.crt
```

## 🛠️ **Manual SSL Configuration**

If your SSL certificates are in different locations, manually update the Apache configuration:

```bash
sudo nano /etc/httpd/conf.d/fishing-weather.conf
```

Update these lines with your actual certificate paths:

```apache
# SSL Configuration (update these paths)
SSLCertificateFile /path/to/your/certificate.crt
SSLCertificateKeyFile /path/to/your/private.key
SSLCertificateChainFile /path/to/your/chain.crt  # Optional
```

## 🔄 **SSL Certificate Renewal**

### **Let's Encrypt Auto-Renewal**
If using Let's Encrypt, certificates auto-renew. Test renewal:

```bash
sudo certbot renew --dry-run
```

### **Manual Renewal**
For other certificates, renew manually and restart Apache:

```bash
sudo systemctl restart httpd
```

## 🧪 **Testing SSL Configuration**

### **Test HTTPS Connectivity**
```bash
# Test the portal
curl -k https://fishing.thepeaveys.net/api/health

# Test with certificate verification
curl https://fishing.thepeaveys.net/api/health
```

### **Check SSL Certificate**
```bash
# View certificate details
openssl s_client -connect fishing.thepeaveys.net:443 -servername fishing.thepeaveys.net

# Check certificate expiration
openssl x509 -in /etc/letsencrypt/live/fishing.thepeaveys.net/cert.pem -noout -dates
```

## 🔒 **Security Headers**

The portal includes these security headers:

```apache
# Security headers (automatically configured)
Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
Header always set X-Content-Type-Options nosniff
Header always set X-Frame-Options DENY
Header always set X-XSS-Protection "1; mode=block"
Header always set Referrer-Policy "strict-origin-when-cross-origin"
```

## 🚨 **Troubleshooting SSL Issues**

### **Common SSL Problems**

1. **Certificate Not Found**
   ```bash
   # Check certificate location
   sudo find /etc -name "*fishing.thepeaveys.net*" 2>/dev/null
   ```

2. **Permission Issues**
   ```bash
   # Fix certificate permissions
   sudo chmod 644 /etc/ssl/certs/fishing.thepeaveys.net.crt
   sudo chmod 600 /etc/ssl/private/fishing.thepeaveys.net.key
   ```

3. **Apache SSL Module Not Loaded**
   ```bash
   # Enable SSL module
   sudo dnf install -y mod_ssl
   sudo systemctl restart httpd
   ```

4. **Firewall Blocking HTTPS**
   ```bash
   # Allow HTTPS traffic
   sudo firewall-cmd --permanent --add-service=https
   sudo firewall-cmd --reload
   ```

### **SSL Error Logs**
```bash
# Check Apache SSL error logs
sudo tail -f /var/log/httpd/fishing-weather-ssl-error.log

# Check Apache access logs
sudo tail -f /var/log/httpd/fishing-weather-ssl-access.log
```

## 📊 **SSL Status Monitoring**

### **Check SSL Certificate Status**
```bash
# Create SSL status check script
cat > check-ssl-status.sh << 'EOF'
#!/bin/bash
echo "🔒 SSL Certificate Status for fishing.thepeaveys.net"
echo "=================================================="

# Check certificate expiration
if [ -f "/etc/letsencrypt/live/fishing.thepeaveys.net/cert.pem" ]; then
    echo "📅 Certificate expires:"
    openssl x509 -in /etc/letsencrypt/live/fishing.thepeaveys.net/cert.pem -noout -enddate
elif [ -f "/etc/ssl/certs/fishing.thepeaveys.net.crt" ]; then
    echo "📅 Certificate expires:"
    openssl x509 -in /etc/ssl/certs/fishing.thepeaveys.net.crt -noout -enddate
else
    echo "❌ Certificate not found"
fi

# Test HTTPS connectivity
echo ""
echo "🌐 HTTPS Connectivity:"
if curl -s -k https://fishing.thepeaveys.net/api/health > /dev/null; then
    echo "✅ HTTPS is working"
else
    echo "❌ HTTPS is not working"
fi
EOF

chmod +x check-ssl-status.sh
```

## 🎉 **SSL Setup Complete!**

Your fishing weather portal is now configured with SSL/HTTPS support:

- ✅ **Secure Access**: https://fishing.thepeaveys.net
- ✅ **Automatic Redirects**: HTTP → HTTPS
- ✅ **Security Headers**: HSTS, XSS protection, etc.
- ✅ **Certificate Management**: Auto-renewal (Let's Encrypt)
- ✅ **Monitoring**: SSL status checks

**🔒 Your portal is now production-ready with enterprise-grade security!**
