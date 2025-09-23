#!/usr/bin/env pwsh

Write-Host "🚀 Deploying migration fix to DigitalOcean droplet..." -ForegroundColor Green

# SSH commands to run on the droplet
$commands = @(
    "cd /opt/UEhub",
    "git pull origin main",
    "cd backend", 
    "docker stop uehub-backend",
    "docker rm uehub-backend",
    "docker build -t uehub-backend .",
    "docker run -d --name uehub-backend --restart unless-stopped -p 8080:8080 --env-file .env uehub-backend",
    "sleep 5",
    "docker exec -it uehub-backend python -m alembic upgrade head",
    "docker logs uehub-backend --tail 20"
)

$sshCommand = $commands -join " && "

Write-Host "Executing deployment commands..." -ForegroundColor Yellow
ssh root@165.22.12.246 $sshCommand

Write-Host "✅ Deployment complete! Testing health check..." -ForegroundColor Green
ssh root@165.22.12.246 "curl -f http://localhost:8080/healthz"
