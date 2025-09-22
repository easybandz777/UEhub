#!/bin/bash
# Complete UE Hub Domain Fix - honestroofingcompany@gmail.com
# This script fixes the domain access issue for echelonx.tech

echo ' Fixing UE Hub domain access for echelonx.tech...'

# Navigate to project directory
cd /opt/uehub || { echo 'Error: /opt/uehub not found'; exit 1; }

# Stop current containers
echo ' Stopping current containers...'
docker-compose down 2>/dev/null || true

# Create proper nginx configuration with domain support
echo ' Creating nginx configuration...'
cat > nginx.conf << 'NGINX_EOF'
events {
    worker_connections 1024;
}

http {
    upstream frontend {
        server frontend:3000;
    }
    
    upstream backend {
        server backend:8080;
    }
    
    server {
        listen 80;
        server_name echelonx.tech www.echelonx.tech uehub.echelonx.tech 165.22.12.246 localhost;
        
        # Backend API routes
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Health checks
        location /health {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        # Frontend routes (everything else)
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
NGINX_EOF

# Create updated docker-compose with domain support
echo ' Creating docker-compose configuration...'
cat > docker-compose.yml << 'COMPOSE_EOF'
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - frontend
      - backend
    restart: unless-stopped

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend.minimal
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_API_URL=/api
    restart: unless-stopped

  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    environment:
      - DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_EoVzn0WyqX1v@ep-odd-tree-adxsa81s-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require
      - SECRET_KEY=uehub-super-secret-production-key-minimum-32-characters-long
      - ENVIRONMENT=production
      - DEBUG=false
    depends_on:
      - redis
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped
COMPOSE_EOF

# Start the services with domain support
echo ' Starting UE Hub with domain support...'
docker-compose up -d --build

# Wait for services to start
echo ' Waiting for services to start...'
sleep 30

# Check status
echo ' Service Status:'
docker-compose ps

# Test the deployment
echo ' Testing deployment...'
curl -I http://localhost || echo 'Local test failed'

echo ''
echo ' UE Hub Domain Fix Complete!'
echo ' Your site should now be accessible at:'
echo '   - http://echelonx.tech'
echo '   - http://www.echelonx.tech'  
echo '   - http://uehub.echelonx.tech'
echo ''
echo ' Monitor with: docker-compose logs -f'
echo ' Restart with: docker-compose restart'
