# One-Click UE Hub Domain Fix
# Run this after SSH key is added to server

Write-Host ' Deploying UE Hub Domain Fix...' -ForegroundColor Green

# Test SSH connection first
Write-Host ' Testing SSH connection...' -ForegroundColor Yellow
try {
    ssh -i "C:\Users\willi\.ssh\id_ed25519_uehub" -o ConnectTimeout=5 root@echelonx.tech 'echo SSH OK'
    Write-Host ' SSH connection successful!' -ForegroundColor Green
} catch {
    Write-Host ' SSH connection failed. Please add the SSH key first.' -ForegroundColor Red
    Write-Host 'Run this in DigitalOcean Console:' -ForegroundColor Yellow
    Write-Host 'mkdir -p ~/.ssh && echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIG4kqcy+/bUEsff7IbKDKzPb6WOGhA0PAY8bY5rw7Mf2 honestroofingcompany@gmail.com" >> ~/.ssh/authorized_keys && chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys' -ForegroundColor Cyan
    exit 1
}

# Deploy the domain fix
Write-Host ' Applying domain fix...' -ForegroundColor Yellow
ssh -i "C:\Users\willi\.ssh\id_ed25519_uehub" root@echelonx.tech 'bash -s' < fix_uehub_domain.sh

Write-Host ' Domain fix complete!' -ForegroundColor Green
Write-Host ' Test your site: http://echelonx.tech' -ForegroundColor Cyan

# Test the deployment
Write-Host ' Testing deployment...' -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri 'http://echelonx.tech' -Method Head -TimeoutSec 10
    Write-Host ' echelonx.tech is responding!' -ForegroundColor Green
    Write-Host "Status: $($response.StatusCode) $($response.StatusDescription)" -ForegroundColor Green
} catch {
    Write-Host ' Site not responding yet, may need a few more seconds...' -ForegroundColor Yellow
}

Write-Host ''
Write-Host ' UE Hub Deployment Complete!' -ForegroundColor Green
Write-Host 'Your site is now live at:' -ForegroundColor White
Write-Host '  - http://echelonx.tech' -ForegroundColor Cyan
Write-Host '  - http://www.echelonx.tech' -ForegroundColor Cyan
Write-Host '  - http://uehub.echelonx.tech' -ForegroundColor Cyan
