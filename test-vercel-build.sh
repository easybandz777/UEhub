#!/bin/bash

echo "🧪 Testing Vercel build locally..."
echo "================================"

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf frontend/.next
rm -rf frontend/node_modules

# Run the exact Vercel build command
echo "📦 Running Vercel build command..."
cd frontend && pnpm install --no-frozen-lockfile && pnpm run build

if [ $? -eq 0 ]; then
    echo "✅ Build successful! Ready to deploy to Vercel."
else
    echo "❌ Build failed. Check the errors above."
    exit 1
fi
