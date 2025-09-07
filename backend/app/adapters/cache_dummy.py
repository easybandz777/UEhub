"""
Dummy cache service adapter for development when Redis is not available.
"""

from typing import Optional, Any
from ..core.interfaces import CacheService


class DummyCacheService(CacheService):
    """Dummy cache service that doesn't actually cache anything."""
    
    async def get(self, key: str) -> Optional[str]:
        """Always return None (cache miss)."""
        return None
    
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """Always return True but don't actually store anything."""
        return True
    
    async def delete(self, key: str) -> bool:
        """Always return True but don't actually delete anything."""
        return True
    
    async def exists(self, key: str) -> bool:
        """Always return False (key doesn't exist)."""
        return False
    
    async def clear(self) -> bool:
        """Always return True but don't actually clear anything."""
        return True
    
    async def ping(self) -> bool:
        """Always return True (dummy service is always available)."""
        return True
