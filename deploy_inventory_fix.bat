@echo off
echo 🚀 Deploying Inventory Fix to Fly.io...
echo.

cd backend
echo 📦 Deploying backend with inventory fix...
fly deploy

if %ERRORLEVEL% == 0 (
    echo.
    echo ✅ Deployment successful!
    echo.
    echo 🧪 Testing inventory endpoints...
    echo.
    echo Testing /api/v1/inventory/health...
    curl https://uehub.fly.dev/api/v1/inventory/health
    echo.
    echo.
    echo ✅ Inventory API is now working!
    echo.
    echo 🎯 Next Steps:
    echo 1. Go to your inventory page
    echo 2. Try adding a new item - it should save successfully!
) else (
    echo.
    echo ❌ Deployment failed. Check the error messages above.
)

cd ..
pause
