# Emergency Backend Deployment Script
Write-Host "🚨 EMERGENCY BACKEND DEPLOYMENT TO FLY.IO" -ForegroundColor Red
Write-Host "=========================================" -ForegroundColor Red
Write-Host ""

# Check if Fly CLI is installed
$flyInstalled = Get-Command fly -ErrorAction SilentlyContinue
if (-not $flyInstalled) {
    Write-Host "📦 Installing Fly CLI..." -ForegroundColor Yellow
    # Install Fly CLI
    powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
    
    # Refresh PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    
    Write-Host "✅ Fly CLI installed!" -ForegroundColor Green
} else {
    Write-Host "✅ Fly CLI already installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "🔐 Logging in to Fly.io..." -ForegroundColor Yellow
Write-Host "If prompted, please authenticate with your Fly.io account" -ForegroundColor Cyan
fly auth login

Write-Host ""
Write-Host "🚀 Deploying Backend with Inventory Fix..." -ForegroundColor Yellow
Write-Host "This will deploy the backend with the inventory endpoints enabled" -ForegroundColor Cyan

# Deploy from root directory (where fly.toml is located)
fly deploy --app uehub

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ BACKEND DEPLOYED SUCCESSFULLY!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🧪 Testing Inventory Endpoints..." -ForegroundColor Yellow
    
    Start-Sleep -Seconds 5
    
    # Test inventory health endpoint
    Write-Host "Testing: https://uehub.fly.dev/api/v1/inventory/health" -ForegroundColor Cyan
    try {
        $response = Invoke-WebRequest -Uri "https://uehub.fly.dev/api/v1/inventory/health" -UseBasicParsing
        Write-Host "Response: $($response.Content)" -ForegroundColor Green
        Write-Host ""
        Write-Host "✅ INVENTORY API IS NOW WORKING!" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Inventory health check failed. The app might still be starting up." -ForegroundColor Yellow
        Write-Host "Wait 30 seconds and try again." -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "🎯 NEXT STEPS:" -ForegroundColor Green
    Write-Host "1. Go to your inventory page: https://u-ehub-n37e65634-william-tyler-beltzs-projects.vercel.app/inventory" -ForegroundColor White
    Write-Host "2. Try adding a new item - it should save successfully!" -ForegroundColor White
    Write-Host ""
    Write-Host "📊 You can also check these endpoints:" -ForegroundColor Cyan
    Write-Host "   - https://uehub.fly.dev/api/v1/inventory/" -ForegroundColor White
    Write-Host "   - https://uehub.fly.dev/api/v1/inventory/stats" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "❌ DEPLOYMENT FAILED!" -ForegroundColor Red
    Write-Host "Please check the error messages above." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "1. Not logged in to Fly.io - run: fly auth login" -ForegroundColor White
    Write-Host "2. App doesn't exist - run: fly apps create uehub" -ForegroundColor White
    Write-Host "3. Missing secrets - run: fly secrets list" -ForegroundColor White
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
