# 🚨 MANUAL BACKEND DEPLOYMENT STEPS

## The Problem
Your inventory isn't working because the backend on Fly.io still has the OLD code where inventory endpoints are disabled. Git push doesn't automatically deploy to Fly.io.

## Quick Fix Steps

### 1. Install Fly CLI (if not installed)
Open PowerShell as Administrator and run:
```powershell
iwr https://fly.io/install.ps1 -useb | iex
```

### 2. Login to Fly.io
```bash
fly auth login
```

### 3. Deploy the Backend
From your project root directory (where fly.toml is located):
```bash
fly deploy --app uehub
```

### 4. Verify Deployment
After deployment completes, test these URLs:

1. **Health Check**: https://uehub.fly.dev/api/v1/inventory/health
   - Should return: `{"status": "healthy", "message": "Inventory router is working"}`

2. **Get Items**: https://uehub.fly.dev/api/v1/inventory/
   - Should return inventory list (even if empty)

3. **Get Stats**: https://uehub.fly.dev/api/v1/inventory/stats
   - Should return stats object

## Alternative: SSH Quick Fix

If deployment is taking too long, you can apply a temporary fix via SSH:

```bash
# 1. SSH into your app
fly ssh console --app uehub

# 2. Edit the file
vi /app/app/api.py

# 3. Go to line 376
:376

# 4. Remove the # comment from the inventory router line
# Change from: # app.include_router(inventory_router...
# To: app.include_router(inventory_router...

# 5. Save and exit
:wq

# 6. Exit SSH
exit

# 7. Restart the app
fly apps restart uehub
```

## Expected Result
Once deployed/fixed:
- ✅ Inventory saves will work
- ✅ All CRUD operations functional
- ✅ No more "Failed to save item" errors

## Still Not Working?
Check the logs:
```bash
fly logs --app uehub
```

Look for any errors related to inventory endpoints.
