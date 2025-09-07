# 🚀 DEPLOY FRONTEND FIX - ELIMINATE DEWALT DRILL

## 🎯 THE PROBLEM
Your Vercel frontend is still using the OLD code that points to `localhost:8000` instead of your Fly.io backend.

## ✅ THE SOLUTION - REDEPLOY FRONTEND

### Method 1: Git Push (Recommended)
```bash
git add .
git commit -m "Fix API URL to use Fly.io backend"
git push origin main
```
Vercel will automatically redeploy when you push to GitHub.

### Method 2: Vercel CLI
```bash
cd frontend
npx vercel --prod
```

### Method 3: Vercel Dashboard
1. Go to https://vercel.com/dashboard
2. Find your project
3. Click "Redeploy"

## 🧪 IMMEDIATE BROWSER FIX (Temporary)

While waiting for deployment, run this in your browser console:

```javascript
// 🔥 FORCE FRONTEND TO USE FLY.IO BACKEND
console.log('🚀 Forcing frontend to use Fly.io backend');

// Override the API base URL
if (window.apiClient) {
  window.apiClient.baseUrl = 'https://uehub.fly.dev';
}

// Override all fetch calls to use Fly.io
const originalFetch = window.fetch;
window.fetch = function(url, options) {
  if (typeof url === 'string' && url.includes('localhost:8000')) {
    url = url.replace('http://localhost:8000', 'https://uehub.fly.dev');
    console.log('🔄 Redirected to Fly.io:', url);
  }
  return originalFetch.call(this, url, options);
};

// Clear cache and reload
localStorage.clear();
sessionStorage.clear();
location.reload(true);
```

## 🎯 VERIFICATION

After redeployment, check:
1. Console should show calls to `https://uehub.fly.dev` (not localhost)
2. No more "ERR_CONNECTION_REFUSED" errors
3. DeWalt drill should be GONE!

The frontend needs to be redeployed with the correct API URL!
