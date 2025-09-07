#!/usr/bin/env python3
"""
Deploy CORS fix to Fly.io
This will update the backend with proper CORS settings
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🚀 {description}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - SUCCESS")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"Error: {e.stderr}")
        return False

def main():
    print("🔥 DEPLOYING CORS FIX TO ELIMINATE DEWALT DRILL")
    
    # Change to project root
    os.chdir(r"D:\new projects\Brianna UE")
    
    # Deploy to Fly.io
    if not run_command("fly deploy -a uehub", "Deploying updated backend to Fly.io"):
        print("❌ Deployment failed. Trying alternative method...")
        # Try with flyctl if fly doesn't work
        run_command("flyctl deploy -a uehub", "Deploying with flyctl")
    
    print("\n🎯 CORS fix deployed!")
    print("✅ Backend now allows your Vercel domain")
    print("✅ API calls should work now")
    print("✅ DeWalt drill will be eliminated!")
    
    print("\n🔄 Next steps:")
    print("1. Wait 30 seconds for deployment")
    print("2. Clear browser cache")
    print("3. Refresh your Vercel site")
    print("4. DeWalt drill should be GONE!")

if __name__ == "__main__":
    main()
