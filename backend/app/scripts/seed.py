"""
Database seeding script.
"""

import asyncio
import logging
from datetime import datetime, timedelta

from app.core.db import get_db_session
from app.modules.auth.repository import AuthRepository

logger = logging.getLogger(__name__)


async def seed_users():
    """Seed initial users."""
    logger.info("Seeding users...")
    
    async with get_db_session() as db:
        auth_repo = AuthRepository(db)
        
        # Check if admin already exists
        admin = await auth_repo.get_by_email("admin@uehub.com")
        if admin:
            logger.info("Admin user already exists, skipping user seeding")
            return
        
        # Create admin user
        admin_data = {
            "email": "admin@uehub.com",
            "name": "System Administrator",
            "role": "admin",
            "password": "Admin123!",
            "is_active": True,
        }
        admin = await auth_repo.create(admin_data)
        logger.info(f"Created admin user: {admin.email}")
        
        # Create manager user
        manager_data = {
            "email": "manager@uehub.com",
            "name": "Operations Manager",
            "role": "manager",
            "password": "Manager123!",
            "is_active": True,
        }
        manager = await auth_repo.create(manager_data)
        logger.info(f"Created manager user: {manager.email}")
        
        # Create worker users
        workers = [
            {
                "email": "worker1@uehub.com",
                "name": "John Worker",
                "role": "worker",
                "password": "Worker123!",
                "is_active": True,
            },
            {
                "email": "worker2@uehub.com",
                "name": "Jane Worker",
                "role": "worker",
                "password": "Worker123!",
                "is_active": True,
            },
        ]
        
        for worker_data in workers:
            worker = await auth_repo.create(worker_data)
            logger.info(f"Created worker user: {worker.email}")


async def seed_inventory():
    """Seed initial inventory items."""
    logger.info("Seeding inventory...")
    
    # This would be implemented when inventory module is complete
    # async with get_db_session() as db:
    #     inventory_repo = InventoryRepository(db)
    #     
    #     items = [
    #         {
    #             "sku": "TOOL-001",
    #             "name": "Safety Helmet",
    #             "qty": 50,
    #             "location": "Warehouse A",
    #             "barcode": "123456789012",
    #             "min_qty": 10,
    #         },
    #         # ... more items
    #     ]
    #     
    #     for item_data in items:
    #         item = await inventory_repo.create(item_data)
    #         logger.info(f"Created inventory item: {item.sku}")
    
    logger.info("Inventory seeding skipped (module not complete)")


async def seed_training():
    """Seed initial training modules."""
    logger.info("Seeding training modules...")
    
    # This would be implemented when training module is complete
    # async with get_db_session() as db:
    #     training_repo = TrainingRepository(db)
    #     
    #     modules = [
    #         {
    #             "title": "Basic Safety Training",
    #             "version": 1,
    #             "content_url": "https://example.com/safety-training",
    #             "duration_min": 30,
    #             "active": True,
    #         },
    #         # ... more modules
    #     ]
    #     
    #     for module_data in modules:
    #         module = await training_repo.create(module_data)
    #         logger.info(f"Created training module: {module.title}")
    
    logger.info("Training seeding skipped (module not complete)")


async def seed_feature_flags():
    """Seed initial feature flags."""
    logger.info("Seeding feature flags...")
    
    # This would be implemented when feature flag module is complete
    # async with get_db_session() as db:
    #     flag_repo = FeatureFlagRepository(db)
    #     
    #     flags = [
    #         {
    #             "key": "inventory",
    #             "enabled": True,
    #             "payload": {"max_items": 10000},
    #         },
    #         {
    #             "key": "training",
    #             "enabled": True,
    #             "payload": {"max_modules": 100},
    #         },
    #         {
    #             "key": "reporting",
    #             "enabled": True,
    #             "payload": {"retention_days": 365},
    #         },
    #         {
    #             "key": "webhooks",
    #             "enabled": True,
    #             "payload": {"max_webhooks": 50},
    #         },
    #     ]
    #     
    #     for flag_data in flags:
    #         flag = await flag_repo.create(flag_data)
    #         logger.info(f"Created feature flag: {flag.key}")
    
    logger.info("Feature flag seeding skipped (module not complete)")


async def main():
    """Main seeding function."""
    logger.info("Starting database seeding...")
    
    try:
        await seed_users()
        await seed_inventory()
        await seed_training()
        await seed_feature_flags()
        
        logger.info("Database seeding completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during seeding: {e}")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
