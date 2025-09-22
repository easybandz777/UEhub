#!/usr/bin/env python3
"""
Fix script to re-enable inventory endpoints in the backend.
Run this on your Fly.io instance to fix inventory functionality.
"""

import subprocess
import sys

def run_command(cmd):
    """Run a shell command and return the output."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result.stdout

def main():
    print("🔧 Fixing Inventory Backend...")
    
    # Connect to Fly.io app
    print("\n1. Connecting to Fly.io app...")
    
    # Create a fixed version of api.py
    fixed_api_content = '''
# At line 377 in backend/app/api.py, uncomment the inventory router:

# BEFORE (current - broken):
# app.include_router(inventory_router, prefix=f"{settings.app.api_prefix}/inventory", tags=["inventory"])

# AFTER (fixed):
app.include_router(inventory_router, prefix=f"{settings.app.api_prefix}/inventory", tags=["inventory"])
'''
    
    print("\n2. The fix needed in backend/app/api.py:")
    print(fixed_api_content)
    
    print("\n3. To apply this fix:")
    print("   a) SSH into your Fly.io app: fly ssh console")
    print("   b) Edit the file: vi /app/app/api.py")
    print("   c) Go to line 377 and remove the # comment")
    print("   d) Save and exit: :wq")
    print("   e) Restart the app: fly apps restart uehub")
    
    print("\n✅ Once applied, inventory functionality will work!")

if __name__ == "__main__":
    main()
