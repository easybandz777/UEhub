#!/bin/bash

# Quick domain fix for UE Hub
echo "🔧 Fixing domain access for echelonx.tech..."

# Stop current containers
echo "Stopping current containers..."
docker-compose down 2>/dev/null || true

# Create updated nginx config
cat > nginx.conf << 'EOF'
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
        
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        location /health {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
EOF

# Update docker-compose to use new nginx config
cat > docker-compose.yml << 'EOF'
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
EOF

# Start with new configuration
echo "Starting with domain-enabled configuration..."
docker-compose up -d --build

echo "✅ Domain fix applied!"
echo "🌐 Test: http://echelonx.tech"
echo "📊 Status: docker-compose ps"
