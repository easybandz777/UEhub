# Deploy Backend Updates to DigitalOcean Droplet
# This script will SSH into the droplet and update the backend

Write-Host "🚀 Deploying Backend Updates to DigitalOcean Droplet..." -ForegroundColor Green

# SSH commands to run on the droplet
$sshCommands = @"
# Navigate to the project directory
cd /opt/UEhub

# Pull latest changes from GitHub
echo "📥 Pulling latest changes..."
git pull origin main

# Navigate to backend directory
cd backend

# Stop the current backend container
echo "🛑 Stopping current backend..."
docker stop uehub-backend 2>/dev/null || true
docker rm uehub-backend 2>/dev/null || true

# Build new backend image
echo "🔨 Building updated backend..."
docker build -t uehub-backend .

# Start the updated backend
echo "🚀 Starting updated backend..."
docker run -d \
  --name uehub-backend \
  --restart unless-stopped \
  -p 8080:8080 \
  --env-file .env \
  uehub-backend

# Check if backend is running
echo "✅ Checking backend status..."
sleep 5
docker ps | grep uehub-backend

# Test the backend health
echo "🏥 Testing backend health..."
curl -f http://localhost:8080/healthz || echo "❌ Health check failed"

echo "✅ Backend deployment complete!"
"@

Write-Host "Commands to run on droplet:" -ForegroundColor Yellow
Write-Host $sshCommands

Write-Host "`n🔑 You'll need to SSH into your droplet and run these commands:" -ForegroundColor Cyan
Write-Host "ssh root@165.22.12.246" -ForegroundColor White

Write-Host "`nOr copy and paste this one-liner:" -ForegroundColor Cyan
$oneLiner = $sshCommands -replace "`n", " && "
Write-Host $oneLiner -ForegroundColor White
