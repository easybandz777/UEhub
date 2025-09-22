# 🚀 Vercel Deployment Fix Guide

## 🎯 Issues Fixed

1. **Package Manager Conflicts**: Removed `package-lock.json` (project uses pnpm)
2. **Duplicate Config**: Removed `frontend/vercel.json` to avoid conflicts
3. **Monorepo Build**: Updated root `vercel.json` with proper build commands
4. **Dependencies**: Added `.npmrc` for proper package resolution

## 📋 Steps to Deploy Successfully

### 1. Clean Local Environment
```bash
# Remove all node_modules and build artifacts
rm -rf node_modules
rm -rf frontend/node_modules
rm -rf frontend/.next
rm -rf packages/*/node_modules

# Install dependencies with pnpm
pnpm install
```

### 2. Test Build Locally
```bash
# Test the exact build command Vercel will use
cd frontend && pnpm install --no-frozen-lockfile && pnpm run build
```

### 3. Set Environment Variables in Vercel Dashboard

Go to your project settings in Vercel and add:

```
NEXT_PUBLIC_API_URL = https://uehub.fly.dev
NEXT_PUBLIC_APP_NAME = UE Hub
NEXT_PUBLIC_APP_VERSION = 1.0.0
```

### 4. Configure Vercel Project Settings

In Vercel Dashboard:
- **Framework Preset**: Next.js
- **Root Directory**: Leave empty (we handle it in vercel.json)
- **Build Command**: Leave empty (using vercel.json)
- **Output Directory**: Leave empty (using vercel.json)
- **Install Command**: Leave empty (using vercel.json)
- **Node.js Version**: 18.x

### 5. Deploy to Vercel

```bash
# Commit all changes
git add .
git commit -m "Fix Vercel deployment configuration"
git push origin main
```

Vercel will automatically redeploy.

## 🔧 Alternative: Deploy Using Vercel CLI

If automatic deployment fails:

```bash
# Install Vercel CLI globally
npm i -g vercel

# Deploy from root directory
vercel --prod
```

When prompted:
- Set up and deploy: Y
- Which scope: (select your account)
- Link to existing project: Y
- What's the name: (your project name)

## 🐛 Common Issues and Solutions

### Issue: "Cannot find module" errors
**Solution**: The `--no-frozen-lockfile` flag in build command handles this

### Issue: "Multiple lockfiles found"
**Solution**: Already fixed by removing package-lock.json

### Issue: Build fails with workspace dependencies
**Solution**: The `.npmrc` file with `shamefully-hoist=true` fixes this

### Issue: API calls fail after deployment
**Solution**: Environment variables are set in vercel.json

## 🧪 Verify Deployment

After deployment:
1. Check build logs in Vercel dashboard
2. Visit your site and open browser console
3. Verify API calls go to `https://uehub.fly.dev` (not localhost)
4. Test login functionality

## 💡 Pro Tips

1. **Clear Vercel Cache**: If build still fails, go to Project Settings → Build & Development Settings → Clear Build Cache

2. **Force Rebuild**: Add `?vercel-no-cache=1` to your deployment URL

3. **Check Build Logs**: Look for specific error messages in Vercel dashboard

4. **Use pnpm Everywhere**: Make sure all team members use pnpm, not npm

## 🎯 Expected Build Output

Your build should show:
```
Installing dependencies with pnpm
Running "cd frontend && pnpm install --no-frozen-lockfile && pnpm run build"
Creating an optimized production build...
Compiled successfully!
```

## 🆘 If Still Having Issues

1. Check that `pnpm-lock.yaml` is committed to git
2. Ensure no `.env` files are committed (they should be in `.gitignore`)
3. Try clearing Vercel build cache and redeploying
4. Check that your git repository is up to date

The deployment should now work! 🎉
