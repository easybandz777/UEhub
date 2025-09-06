"""
Neon database adapter with REST API support.
"""

import json
import logging
from typing import Any, Dict, List, Optional

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.interfaces import Repository
from ..core.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class NeonRestClient:
    """Neon REST API client for serverless functions."""
    
    def __init__(self, api_endpoint: str, api_key: str):
        self.api_endpoint = api_endpoint.rstrip('/')
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            timeout=30.0
        )
    
    async def execute_query(self, query: str, params: Optional[List[Any]] = None) -> Dict[str, Any]:
        """Execute a SQL query via Neon REST API."""
        try:
            payload = {
                "query": query,
                "params": params or []
            }
            
            response = await self.client.post(
                f"{self.api_endpoint}/query",
                json=payload
            )
            
            response.raise_for_status()
            return response.json()
        
        except httpx.HTTPError as e:
            logger.error(f"Neon REST API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in Neon REST API: {e}")
            raise
    
    async def execute_batch(self, queries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute multiple queries in a batch."""
        try:
            payload = {
                "queries": queries
            }
            
            response = await self.client.post(
                f"{self.api_endpoint}/batch",
                json=payload
            )
            
            response.raise_for_status()
            return response.json()
        
        except httpx.HTTPError as e:
            logger.error(f"Neon REST API batch error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in Neon REST API batch: {e}")
            raise
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


class NeonRepository:
    """Base repository with Neon-specific optimizations."""
    
    def __init__(self, db: AsyncSession, table_name: str):
        self.db = db
        self.table_name = table_name
        self._rest_client: Optional[NeonRestClient] = None
    
    @property
    def rest_client(self) -> Optional[NeonRestClient]:
        """Get Neon REST client if configured."""
        if self._rest_client is None and hasattr(settings, 'neon_api_endpoint'):
            if settings.neon_api_endpoint and settings.neon_api_key:
                self._rest_client = NeonRestClient(
                    settings.neon_api_endpoint,
                    settings.neon_api_key
                )
        return self._rest_client
    
    async def execute_raw_query(self, query: str, params: Optional[List[Any]] = None) -> Dict[str, Any]:
        """Execute raw SQL query via REST API (useful for serverless)."""
        if not self.rest_client:
            raise ValueError("Neon REST API not configured")
        
        return await self.rest_client.execute_query(query, params)
    
    async def get_table_stats(self) -> Dict[str, Any]:
        """Get table statistics via REST API."""
        if not self.rest_client:
            # Fallback to SQLAlchemy
            from sqlalchemy import text
            result = await self.db.execute(
                text(f"SELECT COUNT(*) as count FROM {self.table_name}")
            )
            return {"count": result.scalar()}
        
        # Use REST API for better performance in serverless
        result = await self.rest_client.execute_query(
            f"SELECT COUNT(*) as count, pg_total_relation_size('{self.table_name}') as size_bytes FROM {self.table_name}"
        )
        
        if result.get("rows"):
            row = result["rows"][0]
            return {
                "count": row[0],
                "size_bytes": row[1] if len(row) > 1 else None
            }
        
        return {"count": 0, "size_bytes": None}
    
    async def search_full_text(self, search_term: str, columns: List[str]) -> List[Dict[str, Any]]:
        """Full-text search using PostgreSQL's built-in capabilities."""
        if not search_term.strip():
            return []
        
        # Build search query with pg_trgm similarity
        search_columns = " || ' ' || ".join(columns)
        query = f"""
            SELECT *, similarity({search_columns}, %s) as rank
            FROM {self.table_name}
            WHERE {search_columns} %% %s
            ORDER BY rank DESC
            LIMIT 50
        """
        
        if self.rest_client:
            result = await self.rest_client.execute_query(query, [search_term, search_term])
            return result.get("rows", [])
        else:
            # Fallback to SQLAlchemy
            from sqlalchemy import text
            result = await self.db.execute(text(query), {"search_term": search_term})
            return [dict(row._mapping) for row in result.fetchall()]
    
    async def bulk_insert(self, records: List[Dict[str, Any]]) -> int:
        """Bulk insert records efficiently."""
        if not records:
            return 0
        
        if self.rest_client and len(records) > 100:
            # Use REST API for large bulk inserts
            columns = list(records[0].keys())
            placeholders = ", ".join(["%s"] * len(columns))
            query = f"INSERT INTO {self.table_name} ({', '.join(columns)}) VALUES ({placeholders})"
            
            # Batch the inserts
            batch_size = 1000
            total_inserted = 0
            
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                queries = []
                
                for record in batch:
                    queries.append({
                        "query": query,
                        "params": [record[col] for col in columns]
                    })
                
                results = await self.rest_client.execute_batch(queries)
                total_inserted += len([r for r in results if r.get("rowCount", 0) > 0])
            
            return total_inserted
        else:
            # Use SQLAlchemy for smaller batches
            from sqlalchemy import text
            
            columns = list(records[0].keys())
            placeholders = ", ".join([f":{col}" for col in columns])
            query = f"INSERT INTO {self.table_name} ({', '.join(columns)}) VALUES ({placeholders})"
            
            result = await self.db.execute(text(query), records)
            return result.rowcount
    
    async def close(self):
        """Clean up resources."""
        if self._rest_client:
            await self._rest_client.close()


# Neon-optimized settings
class NeonSettings:
    """Neon-specific database settings."""
    
    @staticmethod
    def get_connection_params() -> Dict[str, Any]:
        """Get optimized connection parameters for Neon."""
        return {
            "pool_size": 5,  # Smaller pool for serverless
            "max_overflow": 10,
            "pool_timeout": 30,
            "pool_recycle": 3600,  # 1 hour
            "pool_pre_ping": True,
            "connect_args": {
                "sslmode": "require",
                "application_name": "ue-hub",
                "connect_timeout": 10,
            }
        }
    
    @staticmethod
    def get_serverless_config() -> Dict[str, Any]:
        """Get configuration optimized for serverless deployment."""
        return {
            "pool_size": 1,  # Single connection for serverless
            "max_overflow": 0,
            "pool_timeout": 5,
            "pool_recycle": 300,  # 5 minutes
            "pool_pre_ping": False,  # Skip ping in serverless
        }


# Usage example for repositories
class NeonUserRepository(NeonRepository):
    """User repository with Neon optimizations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, "auth_user")
    
    async def search_users(self, search_term: str) -> List[Dict[str, Any]]:
        """Search users by name or email."""
        return await self.search_full_text(
            search_term, 
            ["name", "email"]
        )
    
    async def get_user_stats(self) -> Dict[str, Any]:
        """Get user statistics."""
        stats = await self.get_table_stats()
        
        # Add role distribution
        if self.rest_client:
            result = await self.rest_client.execute_query(
                "SELECT role, COUNT(*) as count FROM auth_user GROUP BY role"
            )
            role_stats = {row[0]: row[1] for row in result.get("rows", [])}
        else:
            from sqlalchemy import text
            result = await self.db.execute(
                text("SELECT role, COUNT(*) as count FROM auth_user GROUP BY role")
            )
            role_stats = {row.role: row.count for row in result.fetchall()}
        
        stats["roles"] = role_stats
        return stats
