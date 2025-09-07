#!/usr/bin/env python3
"""
Direct table creation script to bypass Alembic migration issues.
"""
import asyncio
import os
from sqlalchemy import text
from app.core.db import async_engine

async def create_inventory_tables():
    """Create inventory tables directly with SQL."""
    
    # SQL to create inventory_items table
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
    
    # SQL to create inventory_events table
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
        async with async_engine.begin() as conn:
            print("Creating inventory_items table...")
            await conn.execute(text(create_inventory_items))
            print("✅ inventory_items table created successfully!")
            
            print("Creating inventory_events table...")
            await conn.execute(text(create_inventory_events))
            print("✅ inventory_events table created successfully!")
            
            print("🎉 All inventory tables created successfully!")
            
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(create_inventory_tables())
