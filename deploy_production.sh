#!/bin/bash

# Deploy UE Hub Production with Caddy
echo "🚀 Deploying UE Hub Production with Caddy..."

# Stop current containers
echo "Stopping current containers..."
docker-compose -f docker-compose.minimal.yml down 2>/dev/null || true

# Deploy with production Caddy setup
echo "Starting production deployment..."
cd infra
DOMAIN=echelonx.tech docker-compose -f docker-compose.prod.yml up -d --build

echo "✅ Production deployment started!"
echo "🌐 Your site will be available at: https://echelonx.tech"
echo "📊 Check status: docker-compose -f infra/docker-compose.prod.yml ps"
