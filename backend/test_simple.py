#!/usr/bin/env python3
"""
Simple test script to test database connectivity and basic API functionality.
"""

import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text

# Set required environment variables
os.environ["DATABASE_URL"] = "postgresql+asyncpg://neondb_owner:npg_EoVzn0WyqX1v@ep-odd-tree-adxsa81s-pooler.c-2.us-east-1.aws.neon.tech/neondb"
os.environ["SECRET_KEY"] = "your-super-secret-key-here-minimum-32-characters-long-for-development-use"

async def test_database_connection():
    """Test basic database connectivity."""
    try:
        # Create engine with SSL settings for Neon
        engine = create_async_engine(
            os.environ["DATABASE_URL"],
            connect_args={"ssl": "require"},
            echo=True
        )
        
        # Create session
        SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with SessionLocal() as session:
            # Test basic query
            result = await session.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            print(f"✅ Database connection successful! Test query result: {row}")
            
            # Test if inventory tables exist
            try:
                result = await session.execute(text("SELECT COUNT(*) FROM inventory_items"))
                count = result.scalar()
                print(f"✅ Inventory table exists with {count} items")
                return True
            except Exception as e:
                print(f"⚠️  Inventory table issue: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

async def test_inventory_endpoints():
    """Test inventory endpoints without full FastAPI app."""
    try:
        from app.modules.inventory.service import InventoryService
        from app.core.db import AsyncSessionLocal
        
        async with AsyncSessionLocal() as session:
            service = InventoryService(session)
            
            # Test getting stats
            stats = await service.get_stats()
            print(f"✅ Inventory stats: {stats}")
            
            # Test listing items
            items = await service.list_items(page=1, per_page=10)
            print(f"✅ Inventory items: {len(items.items)} items found")
            
            return True
            
    except Exception as e:
        print(f"❌ Inventory service test failed: {e}")
        return False

async def main():
    """Run all tests."""
    print("🧪 Starting database integration tests...\n")
    
    # Test 1: Database connection
    print("Test 1: Database Connection")
    db_success = await test_database_connection()
    print()
    
    # Test 2: Inventory endpoints
    if db_success:
        print("Test 2: Inventory Service")
        await test_inventory_endpoints()
        print()
    
    print("🏁 Tests completed!")

if __name__ == "__main__":
    asyncio.run(main())
