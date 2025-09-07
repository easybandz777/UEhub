#!/usr/bin/env python3
"""
Create a default superadmin user for the UE Hub system.
Run this script to create the initial superadmin account.
"""

import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.settings import get_settings
from app.modules.auth.repository import AuthRepository
from app.core.security import get_password_hash

settings = get_settings()

async def create_superadmin():
    """Create the default superadmin user."""
    
    # Database connection
    engine = create_async_engine(
        settings.database.url,
        echo=False,
        pool_pre_ping=True,
        pool_recycle=300,
    )
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        auth_repo = AuthRepository(session)
        
        # Check if superadmin already exists
        existing_admin = await auth_repo.get_by_email("admin@uehub.com")
        if existing_admin:
            print("❌ Superadmin user already exists!")
            print(f"   Email: admin@uehub.com")
            print(f"   Role: {existing_admin.role}")
            print(f"   Active: {existing_admin.is_active}")
            return
        
        # Create superadmin user
        superadmin_data = {
            "email": "admin@uehub.com",
            "name": "System Administrator",
            "password": "SuperAdmin123!",  # This will be hashed
            "role": "superadmin",
            "is_active": True
        }
        
        try:
            user = await auth_repo.create(superadmin_data)
            print("✅ Superadmin user created successfully!")
            print(f"   Email: {user.email}")
            print(f"   Name: {user.name}")
            print(f"   Role: {user.role}")
            print(f"   Password: SuperAdmin123!")
            print("")
            print("🔐 IMPORTANT: Change this password after first login!")
            print("   You can log in at: https://your-domain.com/login")
            print("")
            print("🎯 Superadmin Capabilities:")
            print("   • Create, edit, and delete users")
            print("   • Assign roles (superadmin, admin, employee)")
            print("   • View and approve all safety checklists")
            print("   • Manage safety templates")
            print("   • Full system administration")
            
        except Exception as e:
            print(f"❌ Error creating superadmin user: {e}")
            return
    
    await engine.dispose()

async def create_demo_users():
    """Create demo users for testing."""
    
    engine = create_async_engine(
        settings.database.url,
        echo=False,
        pool_pre_ping=True,
        pool_recycle=300,
    )
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    demo_users = [
        {
            "email": "demo.admin@uehub.com",
            "name": "Demo Admin",
            "password": "DemoAdmin123!",
            "role": "admin"
        },
        {
            "email": "demo.employee@uehub.com", 
            "name": "Demo Employee",
            "password": "DemoEmployee123!",
            "role": "employee"
        }
    ]
    
    async with async_session() as session:
        auth_repo = AuthRepository(session)
        
        print("\n📝 Creating demo users...")
        
        for user_data in demo_users:
            existing_user = await auth_repo.get_by_email(user_data["email"])
            if existing_user:
                print(f"   ⚠️  {user_data['email']} already exists")
                continue
            
            try:
                user_data["is_active"] = True
                user = await auth_repo.create(user_data)
                print(f"   ✅ Created {user.role}: {user.email} (password: {user_data['password']})")
            except Exception as e:
                print(f"   ❌ Error creating {user_data['email']}: {e}")
    
    await engine.dispose()

async def main():
    """Main function."""
    print("🚀 UE Hub - Superadmin Setup")
    print("=" * 40)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--with-demo":
        print("Creating superadmin and demo users...")
        await create_superadmin()
        await create_demo_users()
    else:
        print("Creating superadmin user...")
        await create_superadmin()
        
        print("\n💡 Tip: Run with --with-demo to also create demo users:")
        print("   python create_superadmin.py --with-demo")

if __name__ == "__main__":
    asyncio.run(main())
