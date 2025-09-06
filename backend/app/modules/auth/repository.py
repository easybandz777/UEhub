"""
Authentication module repository.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import Boolean, Column, DateTime, String, and_, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ...core.db import Base
from ...core.interfaces import UserRepository
from ...core.security import get_password_hash, verify_password


class User(Base):
    """User model."""
    
    __tablename__ = "auth_user"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False, default="worker")
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class AuthRepository:
    """Authentication repository implementation."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get(self, id: str) -> Optional[User]:
        """Get user by ID."""
        result = await self.db.execute(
            select(User).where(User.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def list(
        self, 
        *, 
        skip: int = 0, 
        limit: int = 100, 
        filters: Optional[Dict[str, any]] = None
    ) -> List[User]:
        """List users with pagination and filtering."""
        query = select(User)
        
        if filters:
            if "search" in filters and filters["search"]:
                search_term = f"%{filters['search']}%"
                query = query.where(
                    or_(
                        User.name.ilike(search_term),
                        User.email.ilike(search_term)
                    )
                )
            
            if "role" in filters and filters["role"]:
                query = query.where(User.role == filters["role"])
            
            if "is_active" in filters and filters["is_active"] is not None:
                query = query.where(User.is_active == filters["is_active"])
        
        query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def count(self, filters: Optional[Dict[str, any]] = None) -> int:
        """Count users with filters."""
        query = select(func.count(User.id))
        
        if filters:
            if "search" in filters and filters["search"]:
                search_term = f"%{filters['search']}%"
                query = query.where(
                    or_(
                        User.name.ilike(search_term),
                        User.email.ilike(search_term)
                    )
                )
            
            if "role" in filters and filters["role"]:
                query = query.where(User.role == filters["role"])
            
            if "is_active" in filters and filters["is_active"] is not None:
                query = query.where(User.is_active == filters["is_active"])
        
        result = await self.db.execute(query)
        return result.scalar()
    
    async def create(self, data: Dict[str, any]) -> User:
        """Create a new user."""
        # Hash password if provided
        if "password" in data:
            data["password_hash"] = get_password_hash(data.pop("password"))
        
        user = User(**data)
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user
    
    async def update(self, id: str, data: Dict[str, any]) -> Optional[User]:
        """Update an existing user."""
        user = await self.get(id)
        if not user:
            return None
        
        # Hash password if provided
        if "password" in data:
            data["password_hash"] = get_password_hash(data.pop("password"))
        
        for key, value in data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        user.updated_at = datetime.utcnow()
        await self.db.flush()
        await self.db.refresh(user)
        return user
    
    async def delete(self, id: str) -> bool:
        """Delete a user."""
        user = await self.get(id)
        if not user:
            return False
        
        await self.db.delete(user)
        await self.db.flush()
        return True
    
    async def verify_password(self, user: User, password: str) -> bool:
        """Verify user password."""
        return verify_password(password, user.password_hash)
    
    async def get_active_users(self) -> List[User]:
        """Get all active users."""
        result = await self.db.execute(
            select(User).where(User.is_active == True).order_by(User.name)
        )
        return result.scalars().all()
    
    async def get_users_by_role(self, role: str) -> List[User]:
        """Get users by role."""
        result = await self.db.execute(
            select(User).where(
                and_(User.role == role, User.is_active == True)
            ).order_by(User.name)
        )
        return result.scalars().all()
    
    async def deactivate_user(self, id: str) -> Optional[User]:
        """Deactivate a user instead of deleting."""
        return await self.update(id, {"is_active": False})
    
    async def activate_user(self, id: str) -> Optional[User]:
        """Activate a user."""
        return await self.update(id, {"is_active": True})
