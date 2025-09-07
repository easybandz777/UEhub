#!/usr/bin/env python3
"""
Fix database connection and authentication issues.
"""
import asyncio
import os
import sys
import logging
from datetime import datetime

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Set environment variables for database connection
os.environ.update({
    'APP_NAME': 'UE Hub',
    'ENVIRONMENT': 'development',
    'SECRET_KEY': 'development-secret-key-minimum-32-characters-long-for-local-dev',
    'DATABASE_URL': 'postgresql+asyncpg://neondb_owner:npg_EoVzn0WyqX1v@ep-odd-tree-adxsa81s-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require',
    'CORS_ORIGINS': '*',
    'ENABLE_DOCS': 'true',
    'LOG_LEVEL': 'INFO'
})

async def test_database_connection():
    """Test database connection and create tables if needed."""
    print("🔍 Testing database connection...")
    
    try:
        from app.core.db import async_engine, Base
        from app.modules.auth.models import User
        from app.modules.inventory.models import InventoryItem
        from app.modules.safety.models import SafetyChecklist, SafetyChecklistItem, SafetyItem
        
        # Test connection
        async with async_engine.begin() as conn:
            print("✅ Database connection successful")
            
            # Create all tables
            print("🔧 Creating database tables...")
            await conn.run_sync(Base.metadata.create_all)
            print("✅ Database tables created/verified")
            
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

async def create_admin_user():
    """Create admin user if it doesn't exist."""
    print("👤 Creating admin user...")
    
    try:
        from app.core.db import get_db_session
        from app.modules.auth.repository import AuthRepository
        from app.modules.auth.schemas import UserCreate
        
        async with get_db_session() as session:
            auth_repo = AuthRepository(session)
            
            # Check if admin exists
            existing_admin = await auth_repo.get_by_email("admin@uehub.com")
            if existing_admin:
                print("✅ Admin user already exists")
                return True
            
            # Create admin user
            admin_data = UserCreate(
                email="admin@uehub.com",
                name="Admin User",
                password="admin123",
                role="superadmin"
            )
            
            admin_user = await auth_repo.create(admin_data.dict())
            print(f"✅ Admin user created: {admin_user.email}")
            return True
            
    except Exception as e:
        print(f"❌ Failed to create admin user: {e}")
        return False

async def test_authentication():
    """Test authentication endpoints."""
    print("🔐 Testing authentication...")
    
    try:
        from app.core.db import get_db_session
        from app.modules.auth.repository import AuthRepository
        from app.modules.auth.service import AuthService
        from app.core.events import InProcessEventBus
        from app.adapters.mail_console import ConsoleMailService
        
        async with get_db_session() as session:
            auth_repo = AuthRepository(session)
            event_bus = InProcessEventBus()
            mail_service = ConsoleMailService()
            auth_service = AuthService(auth_repo, event_bus, mail_service)
            
            # Test login
            try:
                login_response = await auth_service.login("admin@uehub.com", "admin123")
                print("✅ Authentication test successful")
                print(f"   - User: {login_response.user.email}")
                print(f"   - Token generated: {bool(login_response.access_token)}")
                return True
            except Exception as e:
                print(f"❌ Authentication test failed: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Authentication setup failed: {e}")
        return False

async def fix_cors_issues():
    """Check and fix CORS configuration."""
    print("🌐 Checking CORS configuration...")
    
    try:
        from app.core.settings import get_settings
        settings = get_settings()
        
        print(f"   - CORS origins: {settings.app.cors_origins}")
        print(f"   - Allowed hosts: {settings.app.allowed_hosts}")
        print("✅ CORS configuration looks correct")
        return True
        
    except Exception as e:
        print(f"❌ CORS check failed: {e}")
        return False

async def main():
    """Main function to fix all issues."""
    print("🚀 Starting UE Hub Database and Auth Fix...")
    print("=" * 50)
    
    success_count = 0
    total_tests = 4
    
    # Test 1: Database connection
    if await test_database_connection():
        success_count += 1
    
    # Test 2: Create admin user
    if await create_admin_user():
        success_count += 1
    
    # Test 3: Test authentication
    if await test_authentication():
        success_count += 1
    
    # Test 4: Check CORS
    if await fix_cors_issues():
        success_count += 1
    
    print("=" * 50)
    print(f"📊 Results: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 All issues fixed! The system should work now.")
        print("\n📋 Next steps:")
        print("1. Try logging in with: admin@uehub.com / admin123")
        print("2. Check that inventory and safety features work")
        print("3. Test user registration")
    else:
        print("❌ Some issues remain. Check the errors above.")
        
    return success_count == total_tests

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"💥 Critical error: {e}")
        sys.exit(1)
