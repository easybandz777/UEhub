#!/usr/bin/env python3
"""
Setup production database with all required tables and admin user.
This script can be run on the production server to initialize everything.
"""
import asyncio
import os
import sys
from datetime import datetime
from sqlalchemy import text

# Set environment variables for production
os.environ.update({
    'APP_NAME': 'UE Hub',
    'ENVIRONMENT': 'production',
    'SECRET_KEY': 'production-secret-key-minimum-32-characters-long-for-production',
    'DATABASE_URL': 'postgresql+asyncpg://neondb_owner:npg_EoVzn0WyqX1v@ep-odd-tree-adxsa81s-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require',
    'CORS_ORIGINS': '*',
    'ENABLE_DOCS': 'true',
    'LOG_LEVEL': 'INFO'
})

async def create_auth_tables():
    """Create auth tables directly with SQL."""
    print("🔐 Creating authentication tables...")
    
    create_auth_user = """
    CREATE TABLE IF NOT EXISTS auth_user (
        id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid()::text,
        email VARCHAR(255) UNIQUE NOT NULL,
        name VARCHAR(100) NOT NULL,
        role VARCHAR(20) NOT NULL DEFAULT 'worker',
        password_hash VARCHAR(255) NOT NULL,
        is_active BOOLEAN NOT NULL DEFAULT true,
        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMP NOT NULL DEFAULT NOW()
    );
    
    CREATE INDEX IF NOT EXISTS ix_auth_user_email ON auth_user(email);
    CREATE INDEX IF NOT EXISTS ix_auth_user_role ON auth_user(role);
    CREATE INDEX IF NOT EXISTS ix_auth_user_is_active ON auth_user(is_active);
    """
    
    try:
        # Import here to avoid import errors
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
        from app.core.db import async_engine
        
        async with async_engine.begin() as conn:
            await conn.execute(text(create_auth_user))
            print("✅ Auth tables created successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Error creating auth tables: {e}")
        return False

async def create_inventory_tables():
    """Create inventory tables directly with SQL."""
    print("📦 Creating inventory tables...")
    
    create_inventory_items = """
    CREATE TABLE IF NOT EXISTS inventory_items (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        sku VARCHAR(50) UNIQUE NOT NULL,
        name VARCHAR(200) NOT NULL,
        location VARCHAR(100) NOT NULL,
        barcode VARCHAR(50),
        qty INTEGER NOT NULL DEFAULT 0,
        min_qty INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMP NOT NULL DEFAULT NOW()
    );
    
    CREATE INDEX IF NOT EXISTS ix_inventory_items_sku ON inventory_items(sku);
    CREATE INDEX IF NOT EXISTS ix_inventory_items_name ON inventory_items(name);
    CREATE INDEX IF NOT EXISTS ix_inventory_items_location ON inventory_items(location);
    CREATE INDEX IF NOT EXISTS ix_inventory_items_barcode ON inventory_items(barcode);
    """
    
    create_inventory_events = """
    CREATE TABLE IF NOT EXISTS inventory_events (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        item_id UUID NOT NULL REFERENCES inventory_items(id),
        actor_id VARCHAR(255),
        delta INTEGER NOT NULL,
        reason VARCHAR(200) NOT NULL,
        meta_json JSONB,
        created_at TIMESTAMP NOT NULL DEFAULT NOW()
    );
    
    CREATE INDEX IF NOT EXISTS ix_inventory_events_item_id ON inventory_events(item_id);
    CREATE INDEX IF NOT EXISTS ix_inventory_events_actor_id ON inventory_events(actor_id);
    CREATE INDEX IF NOT EXISTS ix_inventory_events_created_at ON inventory_events(created_at);
    """
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
        from app.core.db import async_engine
        
        async with async_engine.begin() as conn:
            await conn.execute(text(create_inventory_items))
            await conn.execute(text(create_inventory_events))
            print("✅ Inventory tables created successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Error creating inventory tables: {e}")
        return False

async def create_safety_tables():
    """Create safety tables directly with SQL."""
    print("🦺 Creating safety tables...")
    
    create_safety_items = """
    CREATE TABLE IF NOT EXISTS safety_items (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        category VARCHAR(100) NOT NULL,
        number VARCHAR(20) NOT NULL,
        text TEXT NOT NULL,
        is_critical BOOLEAN NOT NULL DEFAULT false,
        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMP NOT NULL DEFAULT NOW()
    );
    
    CREATE INDEX IF NOT EXISTS ix_safety_items_category ON safety_items(category);
    CREATE INDEX IF NOT EXISTS ix_safety_items_number ON safety_items(number);
    CREATE INDEX IF NOT EXISTS ix_safety_items_is_critical ON safety_items(is_critical);
    """
    
    create_safety_checklists = """
    CREATE TABLE IF NOT EXISTS safety_checklists (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        project_name VARCHAR(200) NOT NULL,
        location VARCHAR(200) NOT NULL,
        inspector_id VARCHAR(255) NOT NULL,
        inspection_date DATE NOT NULL,
        scaffold_type VARCHAR(100) NOT NULL,
        height VARCHAR(50) NOT NULL,
        contractor VARCHAR(200),
        permit_number VARCHAR(100),
        status VARCHAR(20) NOT NULL DEFAULT 'draft',
        total_items INTEGER NOT NULL DEFAULT 0,
        passed_items INTEGER NOT NULL DEFAULT 0,
        failed_items INTEGER NOT NULL DEFAULT 0,
        na_items INTEGER NOT NULL DEFAULT 0,
        critical_failures INTEGER NOT NULL DEFAULT 0,
        approved_by_id VARCHAR(255),
        approved_at TIMESTAMP,
        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMP NOT NULL DEFAULT NOW()
    );
    
    CREATE INDEX IF NOT EXISTS ix_safety_checklists_inspector_id ON safety_checklists(inspector_id);
    CREATE INDEX IF NOT EXISTS ix_safety_checklists_status ON safety_checklists(status);
    CREATE INDEX IF NOT EXISTS ix_safety_checklists_inspection_date ON safety_checklists(inspection_date);
    """
    
    create_safety_checklist_items = """
    CREATE TABLE IF NOT EXISTS safety_checklist_items (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        checklist_id UUID NOT NULL REFERENCES safety_checklists(id) ON DELETE CASCADE,
        item_id UUID NOT NULL REFERENCES safety_items(id),
        status VARCHAR(10),
        notes TEXT,
        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMP NOT NULL DEFAULT NOW()
    );
    
    CREATE INDEX IF NOT EXISTS ix_safety_checklist_items_checklist_id ON safety_checklist_items(checklist_id);
    CREATE INDEX IF NOT EXISTS ix_safety_checklist_items_item_id ON safety_checklist_items(item_id);
    CREATE INDEX IF NOT EXISTS ix_safety_checklist_items_status ON safety_checklist_items(status);
    """
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
        from app.core.db import async_engine
        
        async with async_engine.begin() as conn:
            await conn.execute(text(create_safety_items))
            await conn.execute(text(create_safety_checklists))
            await conn.execute(text(create_safety_checklist_items))
            print("✅ Safety tables created successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Error creating safety tables: {e}")
        return False

async def create_admin_user():
    """Create admin user directly with SQL."""
    print("👤 Creating admin user...")
    
    # Hash the password
    import hashlib
    import secrets
    
    password = "Admin123!@#"
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    final_hash = f"pbkdf2_sha256${salt}${password_hash.hex()}"
    
    # Use bcrypt instead for compatibility
    try:
        import bcrypt
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    except ImportError:
        # Fallback to simple hash (not recommended for production)
        password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    create_admin_sql = """
    INSERT INTO auth_user (id, email, name, role, password_hash, is_active, created_at, updated_at)
    VALUES (gen_random_uuid()::text, 'admin@uehub.com', 'Admin User', 'superadmin', %s, true, NOW(), NOW())
    ON CONFLICT (email) DO UPDATE SET
        password_hash = EXCLUDED.password_hash,
        updated_at = NOW();
    """
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
        from app.core.db import async_engine
        
        async with async_engine.begin() as conn:
            await conn.execute(text(create_admin_sql), (password_hash,))
            print("✅ Admin user created successfully!")
            print("🔑 Admin credentials:")
            print("   Email: admin@uehub.com")
            print("   Password: Admin123!@#")
            return True
            
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return False

async def main():
    """Main setup function."""
    print("🚀 Setting up UE Hub Production Database...")
    print("=" * 60)
    
    success_count = 0
    total_steps = 4
    
    # Step 1: Create auth tables
    if await create_auth_tables():
        success_count += 1
    
    # Step 2: Create inventory tables
    if await create_inventory_tables():
        success_count += 1
    
    # Step 3: Create safety tables
    if await create_safety_tables():
        success_count += 1
    
    # Step 4: Create admin user
    if await create_admin_user():
        success_count += 1
    
    print("=" * 60)
    print(f"📊 Setup Results: {success_count}/{total_steps} steps completed")
    
    if success_count == total_steps:
        print("🎉 Database setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Deploy this script to your production server")
        print("2. Run: python setup_production_database.py")
        print("3. Test login with admin@uehub.com / Admin123!@#")
        print("4. Verify all features work correctly")
    else:
        print("❌ Some steps failed. Check the errors above.")
        
    return success_count == total_steps

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"💥 Critical error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
