# Deploy to DigitalOcean App Platform
Write-Host "🚀 Deploying UE Hub to DigitalOcean App Platform..." -ForegroundColor Green

# Check if doctl is installed
$doctlInstalled = Get-Command doctl -ErrorAction SilentlyContinue
if (-not $doctlInstalled) {
    Write-Host "❌ DigitalOcean CLI (doctl) not found!" -ForegroundColor Red
    Write-Host "📦 Install it from: https://docs.digitalocean.com/reference/doctl/how-to/install/" -ForegroundColor Yellow
    Write-Host "Or use the web interface at: https://cloud.digitalocean.com/apps" -ForegroundColor Cyan
    exit 1
}

Write-Host "✅ DigitalOcean CLI found" -ForegroundColor Green

# Deploy the app
Write-Host "📦 Creating app from spec..." -ForegroundColor Yellow
doctl apps create --spec .do/app.yaml

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ App created successfully!" -ForegroundColor Green
    Write-Host "🔗 Check your app at: https://cloud.digitalocean.com/apps" -ForegroundColor Cyan
    
    # Get the app URL
    Write-Host "📋 Getting app info..." -ForegroundColor Yellow
    doctl apps list --format ID,DefaultIngress,Status
    
    Write-Host ""
    Write-Host "🎯 Next Steps:" -ForegroundColor Green
    Write-Host "1. Note the app URL from above" -ForegroundColor White
    Write-Host "2. Update Vercel to point to this new URL" -ForegroundColor White
    Write-Host "3. Set environment variables in DigitalOcean dashboard" -ForegroundColor White
} else {
    Write-Host "❌ Deployment failed!" -ForegroundColor Red
    Write-Host "💡 Try deploying via web interface: https://cloud.digitalocean.com/apps" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
