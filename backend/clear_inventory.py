#!/usr/bin/env python3
"""
Clear all inventory data from the database.
"""
import asyncio
from sqlalchemy import text
from app.core.db import async_engine

async def clear_inventory_data():
    """Clear all inventory data."""
    print("🗑️  Clearing inventory data...")
    
    try:
        async with async_engine.begin() as conn:
            # Clear inventory events first (foreign key constraint)
            await conn.execute(text("DELETE FROM inventory_events"))
            print("✅ Cleared inventory_events table")
            
            # Clear inventory items
            await conn.execute(text("DELETE FROM inventory_items"))
            print("✅ Cleared inventory_items table")
            
            print("🎉 All inventory data cleared successfully!")
            
    except Exception as e:
        print(f"❌ Error clearing inventory data: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(clear_inventory_data())
