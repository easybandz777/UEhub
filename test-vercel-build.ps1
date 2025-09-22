# Test Vercel build locally on Windows
Write-Host "🧪 Testing Vercel build locally..." -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

# Clean previous builds
Write-Host "🧹 Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "frontend\.next") {
    Remove-Item -Path "frontend\.next" -Recurse -Force
}
if (Test-Path "frontend\node_modules") {
    Remove-Item -Path "frontend\node_modules" -Recurse -Force
}

# Run the exact Vercel build command
Write-Host "📦 Running Vercel build command..." -ForegroundColor Yellow
Set-Location frontend
& pnpm install --no-frozen-lockfile
if ($LASTEXITCODE -eq 0) {
    & pnpm run build
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Build successful! Ready to deploy to Vercel." -ForegroundColor Green
    } else {
        Write-Host "❌ Build failed. Check the errors above." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "❌ Install failed. Check the errors above." -ForegroundColor Red
    exit 1
}
Set-Location ..
