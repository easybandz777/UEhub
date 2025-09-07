# 🚀 FLY.IO BACKEND FIX - Complete Commands

## 🎯 THE PROBLEM
Your Fly.io backend is missing the `DATABASE_URL` environment variable, causing inventory API endpoints to fail.

## ✅ SOLUTION COMMANDS

### 1. Set Database URL Secret
```bash
fly secrets set DATABASE_URL="postgresql+asyncpg://neondb_owner:npg_EoVzn0WyqX1v@ep-odd-tree-adxsa81s-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require" -a uehub
```

### 2. Set Secret Key
```bash
fly secrets set SECRET_KEY="development-secret-key-minimum-32-characters-long-for-local-dev" -a uehub
```

### 3. Restart the App
```bash
fly restart -a uehub
```

### 4. Check Status
```bash
fly status -a uehub
fly logs -a uehub --limit 10
```

### 5. Test Endpoints
```bash
# Test health (should work)
curl https://uehub.fly.dev/health

# Test inventory (should work after fix)
curl https://uehub.fly.dev/v1/inventory/
curl https://uehub.fly.dev/v1/inventory/stats
```

## 🧹 BROWSER CACHE CLEARING

After fixing the backend, run this in your browser console on your Vercel site:

```javascript
// DEWALT DRILL KILLER
localStorage.clear();
sessionStorage.clear();
if ('caches' in window) {
  caches.keys().then(names => names.forEach(name => caches.delete(name)));
}
console.log('💀 DeWalt drill eliminated!');
location.reload(true);
```

## 🎯 VERIFICATION
1. Run the Fly.io commands above
2. Wait 30 seconds for deployment
3. Clear browser cache with the script
4. Refresh your Vercel site
5. **DeWalt drill should be GONE!** ✅

The inventory API will return empty data (0 items) instead of failing, eliminating the cached DeWalt drill.
