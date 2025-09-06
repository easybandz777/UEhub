"""
Local file storage adapter.
"""

import os
import shutil
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

from ..core.interfaces import StorageService


class LocalStorageService:
    """Local file system storage implementation."""
    
    def __init__(self, base_path: str, base_url: str = "http://localhost:8000/files/"):
        self.base_path = Path(base_path)
        self.base_url = base_url
        
        # Create base directory if it doesn't exist
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def _get_file_path(self, key: str) -> Path:
        """Get full file path for a key."""
        # Sanitize key to prevent directory traversal
        safe_key = key.replace("..", "").replace("/", "_").replace("\\", "_")
        return self.base_path / safe_key
    
    async def upload(self, key: str, data: bytes, content_type: str) -> str:
        """Upload a file and return its URL."""
        file_path = self._get_file_path(key)
        
        # Create directory if needed
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        with open(file_path, "wb") as f:
            f.write(data)
        
        # Return URL
        return urljoin(self.base_url, key)
    
    async def download(self, key: str) -> bytes:
        """Download a file by key."""
        file_path = self._get_file_path(key)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {key}")
        
        with open(file_path, "rb") as f:
            return f.read()
    
    async def delete(self, key: str) -> None:
        """Delete a file by key."""
        file_path = self._get_file_path(key)
        
        if file_path.exists():
            file_path.unlink()
    
    async def exists(self, key: str) -> bool:
        """Check if a file exists."""
        file_path = self._get_file_path(key)
        return file_path.exists()
    
    async def get_url(self, key: str, expires_in: Optional[int] = None) -> str:
        """Get a URL for a file (ignores expires_in for local storage)."""
        if not await self.exists(key):
            raise FileNotFoundError(f"File not found: {key}")
        
        return urljoin(self.base_url, key)
    
    async def copy(self, source_key: str, dest_key: str) -> str:
        """Copy a file to a new key."""
        source_path = self._get_file_path(source_key)
        dest_path = self._get_file_path(dest_key)
        
        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {source_key}")
        
        # Create destination directory if needed
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy file
        shutil.copy2(source_path, dest_path)
        
        return urljoin(self.base_url, dest_key)
    
    async def move(self, source_key: str, dest_key: str) -> str:
        """Move a file to a new key."""
        source_path = self._get_file_path(source_key)
        dest_path = self._get_file_path(dest_key)
        
        if not source_path.exists():
            raise FileNotFoundError(f"Source file not found: {source_key}")
        
        # Create destination directory if needed
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Move file
        shutil.move(str(source_path), str(dest_path))
        
        return urljoin(self.base_url, dest_key)
    
    async def list_files(self, prefix: str = "") -> list[str]:
        """List files with optional prefix."""
        files = []
        
        if prefix:
            search_path = self.base_path / prefix
            if search_path.is_dir():
                for file_path in search_path.rglob("*"):
                    if file_path.is_file():
                        relative_path = file_path.relative_to(self.base_path)
                        files.append(str(relative_path))
        else:
            for file_path in self.base_path.rglob("*"):
                if file_path.is_file():
                    relative_path = file_path.relative_to(self.base_path)
                    files.append(str(relative_path))
        
        return sorted(files)
    
    async def get_file_size(self, key: str) -> int:
        """Get file size in bytes."""
        file_path = self._get_file_path(key)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {key}")
        
        return file_path.stat().st_size
