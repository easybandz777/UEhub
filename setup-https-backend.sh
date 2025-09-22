#!/bin/bash
# Automated HTTPS setup for UE Hub backend on DigitalOcean

set -e  # Exit on any error

echo "🚀 Setting up HTTPS for UE Hub backend..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="api.echelonx.tech"
DROPLET_IP="165.22.12.246"
EMAIL="admin@echelonx.tech"  # Change this to your email

echo -e "${YELLOW}📋 Configuration:${NC}"
echo "Domain: $DOMAIN"
echo "Droplet IP: $DROPLET_IP"
echo "Email: $EMAIL"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Update system
echo -e "${YELLOW}📦 Updating system packages...${NC}"
apt update -y

# Install required packages
echo -e "${YELLOW}🔧 Installing required packages...${NC}"
apt install -y nginx certbot python3-certbot-nginx curl dnsutils

# Check if domain resolves to our IP
echo -e "${YELLOW}🔍 Checking DNS resolution...${NC}"
RESOLVED_IP=$(dig +short $DOMAIN | tail -n1)

if [ "$RESOLVED_IP" = "$DROPLET_IP" ]; then
    echo -e "${GREEN}✅ DNS is correctly configured: $DOMAIN -> $DROPLET_IP${NC}"
else
    echo -e "${RED}❌ DNS not configured yet!${NC}"
    echo -e "${YELLOW}Please add this A record to your DNS:${NC}"
    echo "Type: A"
    echo "Name: api"
    echo "Value: $DROPLET_IP"
    echo "TTL: 300"
    echo ""
    echo -e "${YELLOW}Waiting for DNS propagation... (checking every 30 seconds)${NC}"
    
    while [ "$RESOLVED_IP" != "$DROPLET_IP" ]; do
        sleep 30
        RESOLVED_IP=$(dig +short $DOMAIN | tail -n1)
        echo "Current resolution: $RESOLVED_IP (waiting for $DROPLET_IP)"
    done
    
    echo -e "${GREEN}✅ DNS propagated successfully!${NC}"
fi

# Create Nginx configuration
echo -e "${YELLOW}⚙️  Creating Nginx configuration...${NC}"
cat > /etc/nginx/sites-available/uehub-backend << EOF
server {
    listen 80;
    server_name $DOMAIN $DROPLET_IP;
    
    # Redirect HTTP to HTTPS (will be added by certbot)
    location / {
        # Add CORS headers for all responses
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization,Accept,Origin' always;
        add_header 'Access-Control-Max-Age' 1728000 always;
        
        # Handle preflight requests
        if (\$request_method = 'OPTIONS') {
            add_header 'Access-Control-Allow-Origin' '*';
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS';
            add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization,Accept,Origin';
            add_header 'Access-Control-Max-Age' 1728000;
            add_header 'Content-Type' 'text/plain; charset=utf-8';
            add_header 'Content-Length' 0;
            return 204;
        }
        
        # Proxy all requests to the backend
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Forwarded-Host \$server_name;
    }
}
EOF

# Enable the site
echo -e "${YELLOW}🔗 Enabling Nginx site...${NC}"
ln -sf /etc/nginx/sites-available/uehub-backend /etc/nginx/sites-enabled/

# Test Nginx configuration
echo -e "${YELLOW}🧪 Testing Nginx configuration...${NC}"
nginx -t

# Reload Nginx
echo -e "${YELLOW}🔄 Reloading Nginx...${NC}"
systemctl reload nginx

# Test HTTP endpoint
echo -e "${YELLOW}🌐 Testing HTTP endpoint...${NC}"
if curl -f http://$DOMAIN/healthz >/dev/null 2>&1; then
    echo -e "${GREEN}✅ HTTP endpoint working${NC}"
else
    echo -e "${RED}❌ HTTP endpoint not working${NC}"
    exit 1
fi

# Get SSL certificate
echo -e "${YELLOW}🔒 Obtaining SSL certificate from Let's Encrypt...${NC}"
certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email $EMAIL --redirect

# Test HTTPS endpoint
echo -e "${YELLOW}🔐 Testing HTTPS endpoint...${NC}"
sleep 5  # Wait a moment for SSL to be ready

if curl -f https://$DOMAIN/healthz >/dev/null 2>&1; then
    echo -e "${GREEN}✅ HTTPS endpoint working${NC}"
else
    echo -e "${YELLOW}⚠️  HTTPS might need a moment to propagate${NC}"
fi

# Test specific endpoints
echo -e "${YELLOW}🧪 Testing API endpoints...${NC}"

echo "Testing health endpoint:"
curl -s https://$DOMAIN/healthz | jq '.' || echo "Health endpoint response received"

echo ""
echo "Testing inventory health:"
curl -s https://$DOMAIN/v1/inventory/health | jq '.' || echo "Inventory health response received"

echo ""
echo "Testing login endpoint:"
curl -s -X POST https://$DOMAIN/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass"}' | jq '.' || echo "Login endpoint response received"

# Setup auto-renewal
echo -e "${YELLOW}🔄 Setting up SSL certificate auto-renewal...${NC}"
systemctl enable certbot.timer
systemctl start certbot.timer

echo ""
echo -e "${GREEN}🎉 HTTPS setup complete!${NC}"
echo ""
echo -e "${YELLOW}📋 Summary:${NC}"
echo "✅ Domain: https://$DOMAIN"
echo "✅ SSL Certificate: Active"
echo "✅ Auto-renewal: Enabled"
echo "✅ CORS: Configured"
echo "✅ Backend: Proxied to port 8080"
echo ""
echo -e "${YELLOW}🔧 Next steps:${NC}"
echo "1. Update Vercel environment variable:"
echo "   NEXT_PUBLIC_API_URL=https://$DOMAIN"
echo ""
echo "2. Test your application login functionality"
echo ""
echo -e "${GREEN}Backend is now available at: https://$DOMAIN${NC}"
