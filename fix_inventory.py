#!/usr/bin/env python3
"""
Complete fix for the inventory "1 tool" issue.
This script will:
1. Start the backend server
2. Test API connectivity  
3. Clear frontend cache
4. Verify the fix
"""
import os
import sys
import time
import subprocess
import requests
from pathlib import Path

def print_step(step, message):
    print(f"\n🔧 Step {step}: {message}")

def start_backend():
    """Start the backend server."""
    print_step(1, "Starting backend server...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found!")
        return False
    
    # Set environment variables
    env = os.environ.copy()
    env.update({
        'APP_NAME': 'UE Hub',
        'ENVIRONMENT': 'development',
        'SECRET_KEY': 'development-secret-key-minimum-32-characters-long-for-local-dev',
        'DATABASE_URL': 'postgresql+asyncpg://neondb_owner:npg_EoVzn0WyqX1v@ep-odd-tree-adxsa81s-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require',
        'CORS_ORIGINS': 'http://localhost:3000,http://localhost:3001',
        'ENABLE_DOCS': 'true',
        'LOG_LEVEL': 'INFO'
    })
    
    try:
        # Start server in background
        process = subprocess.Popen([
            "py", "-m", "uvicorn", "app.api:app",
            "--host", "0.0.0.0", "--port", "8000", "--reload"
        ], cwd=backend_dir, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("⏳ Waiting for server to start...")
        time.sleep(8)  # Give it more time
        
        return process
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None

def test_backend():
    """Test if backend is responding."""
    print_step(2, "Testing backend connectivity...")
    
    for attempt in range(5):
        try:
            response = requests.get("http://localhost:8000/health", timeout=10)
            if response.status_code == 200:
                print("✅ Backend health check passed!")
                print(f"📊 Response: {response.json()}")
                return True
        except Exception as e:
            print(f"⏳ Attempt {attempt + 1}/5 failed: {e}")
            time.sleep(2)
    
    print("❌ Backend not responding after 5 attempts")
    return False

def test_inventory_api():
    """Test inventory API endpoints."""
    print_step(3, "Testing inventory API...")
    
    try:
        # Test inventory list
        response = requests.get("http://localhost:8000/v1/inventory/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Inventory API working! Found {len(data.get('items', []))} items")
            return True
        else:
            print(f"❌ Inventory API returned status {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Inventory API test failed: {e}")
        return False

def create_cache_clear_script():
    """Create a script to clear browser cache."""
    print_step(4, "Creating cache clear script...")
    
    script_content = '''
// COPY AND PASTE THIS INTO YOUR BROWSER CONSOLE
console.log("🗑️ CLEARING ALL CACHE...");

// Clear localStorage
localStorage.removeItem('inventory-items');
localStorage.removeItem('inventory-stats');
localStorage.clear();

// Clear sessionStorage
sessionStorage.clear();

console.log("✅ Cache cleared!");
console.log("🔄 Now do a HARD REFRESH: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)");

// Test API
fetch('http://localhost:8000/v1/inventory/')
    .then(response => response.json())
    .then(data => {
        console.log("✅ API Test Result:", data);
        console.log(`📊 Items found: ${data.items ? data.items.length : 0}`);
    })
    .catch(error => {
        console.log("❌ API Test Failed:", error);
    });
'''
    
    with open("CLEAR_CACHE.js", "w") as f:
        f.write(script_content)
    
    print("✅ Created CLEAR_CACHE.js")
    return True

def main():
    """Main fix process."""
    print("🚀 FIXING INVENTORY '1 TOOL' ISSUE")
    print("=" * 50)
    
    # Start backend
    process = start_backend()
    if not process:
        print("💥 Failed to start backend!")
        return False
    
    # Test backend
    if not test_backend():
        print("💥 Backend not responding!")
        return False
    
    # Test inventory API
    if not test_inventory_api():
        print("💥 Inventory API not working!")
        return False
    
    # Create cache clear script
    create_cache_clear_script()
    
    print("\n" + "=" * 50)
    print("🎉 BACKEND IS RUNNING!")
    print("📋 Next steps:")
    print("1. Open your browser to the inventory page")
    print("2. Open DevTools (F12)")
    print("3. Go to Console tab")
    print("4. Copy and paste the contents of CLEAR_CACHE.js")
    print("5. Press Enter")
    print("6. Do a hard refresh (Ctrl+Shift+R)")
    print("\n✅ The '1 tool' issue should be fixed!")
    print("🔗 Backend: http://localhost:8000")
    print("📋 API Docs: http://localhost:8000/docs")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n⏳ Backend is running. Press Ctrl+C to stop.")
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Stopping...")
    except Exception as e:
        print(f"\n💥 Error: {e}")
        sys.exit(1)
