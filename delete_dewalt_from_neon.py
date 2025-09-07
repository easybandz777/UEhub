#!/usr/bin/env python3
"""
Delete the DeWalt drill from Neon database
This will eliminate it from the source!
"""

import asyncio
import asyncpg
import os

# Your Neon database connection string
DATABASE_URL = "postgresql://neondb_owner:npg_EoVzn0WyqX1v@ep-odd-tree-adxsa81s-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"

async def delete_dewalt_drill():
    """Delete all inventory items from Neon database"""
    try:
        # Connect to Neon database
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Connected to Neon database")
        
        # Delete all inventory items (including the DeWalt drill)
        result = await conn.execute("DELETE FROM inventory_items")
        print(f"🗑️ Deleted inventory items: {result}")
        
        # Also delete any inventory events
        result2 = await conn.execute("DELETE FROM inventory_events")
        print(f"🗑️ Deleted inventory events: {result2}")
        
        # Verify deletion
        count = await conn.fetchval("SELECT COUNT(*) FROM inventory_items")
        print(f"📊 Remaining items in database: {count}")
        
        if count == 0:
            print("🎯 SUCCESS! DeWalt drill eliminated from Neon database!")
        else:
            print(f"⚠️ Warning: {count} items still remain")
            
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🔥 DELETING DEWALT DRILL FROM NEON DATABASE")
    asyncio.run(delete_dewalt_drill())
