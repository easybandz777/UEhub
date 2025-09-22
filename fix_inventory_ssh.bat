@echo off
echo Fixing inventory via SSH...
echo.

REM SSH into the app and fix the inventory router
"%USERPROFILE%\.fly\bin\flyctl.exe" ssh console --app uehub --command "sed -i '376s/^# //' /app/app/api.py && echo 'Fixed inventory router'"

echo.
echo Restarting the app...
"%USERPROFILE%\.fly\bin\flyctl.exe" apps restart uehub

echo.
echo Testing inventory endpoint...
timeout /t 10
curl https://uehub.fly.dev/api/v1/inventory/health

echo.
pause
