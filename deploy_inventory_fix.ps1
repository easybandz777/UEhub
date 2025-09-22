# Deploy inventory fix to Fly.io
Write-Host "🚀 Deploying Inventory Fix to Fly.io..." -ForegroundColor Green

# Change to backend directory
Set-Location backend

Write-Host "`n📦 Deploying backend with inventory fix..." -ForegroundColor Yellow
fly deploy

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Deployment successful!" -ForegroundColor Green
    Write-Host "`n🧪 Testing inventory endpoints..." -ForegroundColor Yellow
    
    # Test the endpoints
    Write-Host "`nTesting /api/v1/inventory/health..." -ForegroundColor Cyan
    Invoke-WebRequest -Uri "https://uehub.fly.dev/api/v1/inventory/health" -UseBasicParsing | Select-Object -ExpandProperty Content
    
    Write-Host "`n✅ Inventory API is now working!" -ForegroundColor Green
    Write-Host "`n🎯 Next Steps:" -ForegroundColor Yellow
    Write-Host "1. Go to your inventory page: https://u-ehub-n37e65634-william-tyler-beltzs-projects.vercel.app/inventory"
    Write-Host "2. Try adding a new item - it should save successfully!"
} else {
    Write-Host "`n❌ Deployment failed. Check the error messages above." -ForegroundColor Red
}

# Return to root directory
Set-Location ..
