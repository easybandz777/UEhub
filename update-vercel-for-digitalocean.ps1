# Update Vercel to use DigitalOcean backend
Write-Host "🔧 Configuring Vercel for DigitalOcean backend..." -ForegroundColor Green

# Prompt for DigitalOcean app URL
$doUrl = Read-Host "Enter your DigitalOcean app URL (e.g., https://uehub-backend-xxxxx.ondigitalocean.app)"

if (-not $doUrl) {
    Write-Host "❌ URL is required!" -ForegroundColor Red
    exit 1
}

# Remove trailing slash if present
$doUrl = $doUrl.TrimEnd('/')

Write-Host "📝 Updating configuration files..." -ForegroundColor Yellow

# Update vercel.json
$vercelConfig = @{
    version = 2
    framework = "nextjs"
    outputDirectory = "frontend/.next"
    env = @{
        NEXT_PUBLIC_API_URL = $doUrl
        NEXT_PUBLIC_APP_NAME = "UE Hub"
        NEXT_PUBLIC_APP_VERSION = "1.0.0"
    }
    build = @{
        env = @{
            NEXT_PUBLIC_API_URL = $doUrl
            NEXT_PUBLIC_APP_NAME = "UE Hub"
            NEXT_PUBLIC_APP_VERSION = "1.0.0"
        }
    }
}

$vercelConfig | ConvertTo-Json -Depth 10 | Out-File -FilePath "vercel.json" -Encoding UTF8

Write-Host "✅ Updated vercel.json" -ForegroundColor Green

Write-Host ""
Write-Host "🎯 Next Steps:" -ForegroundColor Green
Write-Host "1. Commit and push changes: git add . && git commit -m 'Update API URL for DigitalOcean' && git push" -ForegroundColor White
Write-Host "2. Vercel will automatically redeploy with new backend URL" -ForegroundColor White
Write-Host "3. Test your inventory at: https://your-vercel-url.vercel.app/inventory" -ForegroundColor White

Write-Host ""
Write-Host "🔗 Your backend will be at: $doUrl" -ForegroundColor Cyan
Write-Host "🔗 Test inventory endpoint: $doUrl/v1/inventory/health" -ForegroundColor Cyan
