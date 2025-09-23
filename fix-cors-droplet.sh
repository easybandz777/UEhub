#!/bin/bash

echo "🔧 Fixing CORS issues on DigitalOcean Droplet..."

# Backup current nginx config
echo "📋 Backing up current nginx configuration..."
cp /etc/nginx/sites-available/uehub-backend /etc/nginx/sites-available/uehub-backend.backup.$(date +%Y%m%d_%H%M%S)

# Remove ALL CORS headers from ALL nginx configs
echo "🧹 Removing all CORS headers from nginx configurations..."
find /etc/nginx -name "*.conf" -o -name "*" -path "*/sites-*/*" | xargs grep -l "Access-Control" 2>/dev/null | while read file; do
    echo "  Cleaning $file"
    sed -i '/add_header.*Access-Control/d' "$file"
done

# Remove OPTIONS blocks from ALL nginx configs
echo "🧹 Removing all OPTIONS blocks from nginx configurations..."
find /etc/nginx -name "*.conf" -o -name "*" -path "*/sites-*/*" | xargs grep -l "OPTIONS" 2>/dev/null | while read file; do
    echo "  Cleaning OPTIONS from $file"
    # Remove entire if blocks that handle OPTIONS
    sed -i '/if.*request_method.*OPTIONS/,/}/d' "$file"
done

# Create clean uehub-backend config
echo "📝 Creating clean uehub-backend nginx configuration..."
cat > /etc/nginx/sites-available/uehub-backend << 'EOF'
server {
    listen 80;
    server_name api.echelonx.tech 165.22.12.246;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.echelonx.tech 165.22.12.246;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/api.echelonx.tech/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.echelonx.tech/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    location / {
        # Forward the original Origin header to backend
        proxy_set_header Origin $http_origin;
        
        # Pass through CORS headers from backend (don't add our own)
        proxy_pass_header Access-Control-Allow-Origin;
        proxy_pass_header Access-Control-Allow-Methods;
        proxy_pass_header Access-Control-Allow-Headers;
        proxy_pass_header Access-Control-Allow-Credentials;
        
        # Standard proxy headers
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $server_name;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF

# Test nginx configuration
echo "🔍 Testing nginx configuration..."
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Nginx configuration is valid"
    
    # Reload nginx
    echo "🔄 Reloading nginx..."
    systemctl reload nginx
    
    echo "✅ Nginx reloaded successfully"
    
    # Test CORS from backend
    echo "🧪 Testing CORS from backend..."
    docker exec uehub-backend curl -sI -X OPTIONS http://localhost:8080/v1/timeclock/job-sites \
        -H "Origin: https://www.echelonx.tech" \
        -H "Access-Control-Request-Method: POST" \
        -H "Access-Control-Request-Headers: authorization, content-type" | grep -i access-control
    
    echo ""
    echo "🧪 Testing external CORS..."
    curl -sI -X OPTIONS https://api.echelonx.tech/v1/timeclock/job-sites \
        -H "Origin: https://www.echelonx.tech" \
        -H "Access-Control-Request-Method: POST" \
        -H "Access-Control-Request-Headers: authorization, content-type" | grep -i access-control
    
    echo ""
    echo "✅ CORS fix completed!"
    echo "🌐 Try accessing the timeclock module from the frontend now."
    
else
    echo "❌ Nginx configuration test failed!"
    echo "🔄 Restoring backup..."
    cp /etc/nginx/sites-available/uehub-backend.backup.* /etc/nginx/sites-available/uehub-backend 2>/dev/null || echo "No backup to restore"
    exit 1
fi
