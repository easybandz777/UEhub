# PowerShell script to update Vercel with HTTPS backend URL

Write-Host "🚀 Updating Vercel configuration for HTTPS backend..." -ForegroundColor Green

# Update vercel.json with HTTPS URL
$vercelConfig = @"
{
  "version": 2,
  "framework": "nextjs",
  "outputDirectory": "frontend/.next",
  "env": {
    "NEXT_PUBLIC_API_URL": "https://api.echelonx.tech",
    "NEXT_PUBLIC_APP_NAME": "UE Hub",
    "NEXT_PUBLIC_APP_VERSION": "1.0.0"
  },
  "build": {
    "env": {
      "NEXT_PUBLIC_API_URL": "https://api.echelonx.tech",
      "NEXT_PUBLIC_APP_NAME": "UE Hub",
      "NEXT_PUBLIC_APP_VERSION": "1.0.0"
    }
  }
}
"@

Write-Host "📝 Updating vercel.json..." -ForegroundColor Yellow
$vercelConfig | Out-File -FilePath "vercel.json" -Encoding UTF8

Write-Host "📋 Committing changes..." -ForegroundColor Yellow
git add vercel.json
git commit -m "Update Vercel to use HTTPS backend URL (api.echelonx.tech)"

Write-Host "🚀 Pushing to trigger Vercel deployment..." -ForegroundColor Yellow
git push origin main

Write-Host ""
Write-Host "✅ Vercel configuration updated!" -ForegroundColor Green
Write-Host "🌐 Backend URL: https://api.echelonx.tech" -ForegroundColor Cyan
Write-Host "⏳ Vercel deployment will start automatically..." -ForegroundColor Yellow
Write-Host ""
Write-Host "🧪 You can test the backend directly:" -ForegroundColor Yellow
Write-Host "   curl https://api.echelonx.tech/healthz" -ForegroundColor Gray
Write-Host "   curl https://api.echelonx.tech/v1/inventory/health" -ForegroundColor Gray
