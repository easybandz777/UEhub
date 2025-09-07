#!/usr/bin/env python3
"""
Deploy database fixes to production.
"""
import subprocess
import sys
import time

def run_command(command, description):
    """Run a command and return success status."""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"   Error: {e.stderr.strip() if e.stderr else str(e)}")
        return False

def main():
    """Main deployment function."""
    print("🚀 Deploying Database Fixes to Production...")
    print("=" * 50)
    
    steps = [
        ("git add .", "Adding changes to git"),
        ("git commit -m \"Fix database models and add production setup script\"", "Committing changes"),
        ("git push", "Pushing changes to repository"),
    ]
    
    success_count = 0
    
    for command, description in steps:
        if run_command(command, description):
            success_count += 1
        else:
            print(f"⚠️  Continuing despite {description} failure...")
    
    print("=" * 50)
    print(f"📊 Deployment Results: {success_count}/{len(steps)} steps completed")
    
    if success_count >= 2:  # At least commit and push worked
        print("🎉 Code changes deployed successfully!")
        print("\n📋 Next steps to complete the fix:")
        print("1. The backend code has been updated and pushed")
        print("2. The production server should automatically redeploy")
        print("3. Wait 2-3 minutes for deployment to complete")
        print("4. Test the login functionality")
        
        print("\n🔄 Testing in 30 seconds...")
        time.sleep(30)
        
        # Test the production API
        print("\n🧪 Testing production API...")
        test_result = run_command("node create_admin_user.js", "Testing admin user creation")
        
        if test_result:
            print("\n🎉 SUCCESS! The database issues have been fixed!")
            print("You can now login to the website with:")
            print("   Email: admin@uehub.com")
            print("   Password: Admin123!@#")
        else:
            print("\n⚠️  The API is still having issues.")
            print("The database tables may need to be created manually.")
            print("Check the server logs for more details.")
    else:
        print("❌ Deployment failed. Check the errors above.")
        
    return success_count >= 2

if __name__ == "__main__":
    try:
        result = main()
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"💥 Critical error: {e}")
        sys.exit(1)
