#!/usr/bin/env python3
"""
Test script to verify API endpoints work.
"""
import asyncio
import json
from app.modules.inventory.service import InventoryService
from app.core.db import AsyncSessionLocal

async def test_inventory_api():
    """Test inventory API functionality."""
    
    async with AsyncSessionLocal() as db:
        service = InventoryService(db)
        
        try:
            # Test getting stats (should work even with empty tables)
            print("Testing inventory stats...")
            stats = await service.get_stats()
            print(f"✅ Stats: {stats}")
            
            # Test getting items (should return empty list)
            print("Testing get items...")
            items = await service.get_items()
            print(f"✅ Items count: {len(items)}")
            
            # Test creating an item
            print("Testing create item...")
            test_item = {
                "sku": "TEST-001",
                "name": "Test Item",
                "location": "Warehouse A",
                "barcode": "123456789",
                "qty": 10,
                "min_qty": 5
            }
            
            created_item = await service.create_item(test_item)
            print(f"✅ Created item: {created_item.sku}")
            
            # Test getting the item back
            print("Testing get item by ID...")
            retrieved_item = await service.get_item_by_id(created_item.id)
            print(f"✅ Retrieved item: {retrieved_item.name}")
            
            print("🎉 All API tests passed!")
            
        except Exception as e:
            print(f"❌ API test failed: {e}")
            raise

if __name__ == "__main__":
    asyncio.run(test_inventory_api())
