"""
Neon database setup script.
"""

import asyncio
import logging
import os
from typing import Dict, Any

from app.adapters.database_neon import NeonRestClient
from app.core.db import async_engine
from app.core.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


async def test_neon_connection():
    """Test the Neon database connection."""
    logger.info("Testing Neon database connection...")
    
    try:
        # Test SQLAlchemy connection
        async with async_engine.connect() as conn:
            result = await conn.execute("SELECT 1 as test")
            row = result.fetchone()
            logger.info(f"✅ SQLAlchemy connection successful: {row}")
        
        # Test REST API if configured
        if settings.database.neon_api_endpoint and settings.database.neon_api_key:
            rest_client = NeonRestClient(
                settings.database.neon_api_endpoint,
                settings.database.neon_api_key
            )
            
            result = await rest_client.execute_query("SELECT 1 as test, NOW() as timestamp")
            logger.info(f"✅ Neon REST API connection successful: {result}")
            
            await rest_client.close()
        else:
            logger.warning("⚠️  Neon REST API not configured (NEON_API_ENDPOINT or NEON_API_KEY missing)")
    
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise


async def setup_neon_extensions():
    """Set up PostgreSQL extensions for Neon."""
    logger.info("Setting up PostgreSQL extensions...")
    
    extensions = [
        "pg_trgm",  # For full-text search
        "uuid-ossp",  # For UUID generation
        "pgcrypto",  # For cryptographic functions
    ]
    
    try:
        async with async_engine.connect() as conn:
            for ext in extensions:
                try:
                    await conn.execute(f"CREATE EXTENSION IF NOT EXISTS \"{ext}\"")
                    logger.info(f"✅ Extension '{ext}' enabled")
                except Exception as e:
                    logger.warning(f"⚠️  Could not enable extension '{ext}': {e}")
            
            await conn.commit()
    
    except Exception as e:
        logger.error(f"❌ Failed to set up extensions: {e}")
        raise


async def optimize_neon_settings():
    """Optimize PostgreSQL settings for Neon."""
    logger.info("Optimizing database settings for Neon...")
    
    # These settings are optimized for Neon's architecture
    settings_queries = [
        # Enable better query planning
        "SET random_page_cost = 1.1",
        "SET effective_cache_size = '1GB'",
        
        # Optimize for concurrent connections
        "SET max_connections = 100",
        
        # Enable better logging (if permissions allow)
        # "SET log_statement = 'all'",  # Uncomment for debugging
    ]
    
    try:
        async with async_engine.connect() as conn:
            for query in settings_queries:
                try:
                    await conn.execute(query)
                    logger.info(f"✅ Applied setting: {query}")
                except Exception as e:
                    logger.warning(f"⚠️  Could not apply setting '{query}': {e}")
    
    except Exception as e:
        logger.error(f"❌ Failed to optimize settings: {e}")


async def create_database_schema():
    """Create the initial database schema."""
    logger.info("Creating database schema...")
    
    try:
        # Import all models to ensure they're registered
        from app.modules.auth.repository import User
        
        # Create all tables
        async with async_engine.begin() as conn:
            # This will create tables based on SQLAlchemy models
            from app.core.db import Base
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("✅ Database schema created successfully")
    
    except Exception as e:
        logger.error(f"❌ Failed to create schema: {e}")
        raise


async def verify_neon_setup():
    """Verify the Neon setup is working correctly."""
    logger.info("Verifying Neon setup...")
    
    try:
        async with async_engine.connect() as conn:
            # Check if tables exist
            result = await conn.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            
            tables = [row[0] for row in result.fetchall()]
            logger.info(f"✅ Found tables: {tables}")
            
            # Check extensions
            result = await conn.execute("""
                SELECT extname 
                FROM pg_extension 
                WHERE extname IN ('pg_trgm', 'uuid-ossp', 'pgcrypto')
            """)
            
            extensions = [row[0] for row in result.fetchall()]
            logger.info(f"✅ Enabled extensions: {extensions}")
            
            # Test full-text search capability
            if 'pg_trgm' in extensions:
                result = await conn.execute("""
                    SELECT 'test' % 'test' as similarity_test,
                           similarity('hello world', 'hello') as similarity_score
                """)
                row = result.fetchone()
                logger.info(f"✅ Full-text search test: {row}")
    
    except Exception as e:
        logger.error(f"❌ Verification failed: {e}")
        raise


async def main():
    """Main setup function."""
    logger.info("🚀 Starting Neon database setup...")
    
    try:
        # Step 1: Test connection
        await test_neon_connection()
        
        # Step 2: Set up extensions
        await setup_neon_extensions()
        
        # Step 3: Optimize settings
        await optimize_neon_settings()
        
        # Step 4: Create schema (if needed)
        # await create_database_schema()  # Uncomment if not using Alembic
        
        # Step 5: Verify setup
        await verify_neon_setup()
        
        logger.info("🎉 Neon database setup completed successfully!")
        
        # Print connection info
        logger.info(f"📊 Database URL: {settings.database.url}")
        if settings.database.neon_api_endpoint:
            logger.info(f"🔗 REST API Endpoint: {settings.database.neon_api_endpoint}")
        
        logger.info("""
Next steps:
1. Run migrations: alembic upgrade head
2. Seed initial data: python -m app.scripts.seed
3. Start the API server: uvicorn app.api:app --reload
        """)
    
    except Exception as e:
        logger.error(f"💥 Setup failed: {e}")
        raise


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    asyncio.run(main())
