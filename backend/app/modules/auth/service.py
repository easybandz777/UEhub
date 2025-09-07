"""
Authentication module service.
"""

import math
from datetime import timedelta
from typing import Dict, List, Optional, Tuple

from fastapi import HTTPException, status

from ...core.events import UserCreatedEvent
from ...core.interfaces import EventBus, MailService
from ...core.security import create_access_token, create_refresh_token, verify_token
from ...core.settings import get_settings
from .repository import AuthRepository, User
from .schemas import (
    LoginResponse,
    RefreshTokenResponse,
    UserCreate,
    UserListResponse,
    UserResponse,
    UserUpdate,
    UserProfile,
)

settings = get_settings()


class AuthService:
    """Authentication service."""
    
    def __init__(
        self, 
        repository: AuthRepository, 
        event_bus: EventBus,
        mail_service: MailService
    ):
        self.repository = repository
        self.event_bus = event_bus
        self.mail_service = mail_service
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user by email and password."""
        user = await self.repository.get_by_email(email)
        if not user or not user.is_active:
            return None
        
        if not await self.repository.verify_password(user, password):
            return None
        
        return user
    
    async def login(self, email: str, password: str) -> LoginResponse:
        """Login a user and return tokens."""
        user = await self.authenticate_user(email, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create tokens
        token_data = {
            "sub": user.id,
            "email": user.email,
            "role": user.role
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.auth.access_token_expire_minutes * 60,
            user=UserResponse.from_orm(user)
        )
    
    async def refresh_token(self, refresh_token: str) -> RefreshTokenResponse:
        """Refresh an access token."""
        try:
            token_data = verify_token(refresh_token)
            
            # Verify user still exists and is active
            user = await self.repository.get(token_data.user_id)
            if not user or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found or inactive"
                )
            
            # Create new access token
            new_token_data = {
                "sub": user.id,
                "email": user.email,
                "role": user.role
            }
            
            access_token = create_access_token(new_token_data)
            
            return RefreshTokenResponse(
                access_token=access_token,
                expires_in=settings.auth.access_token_expire_minutes * 60
            )
        
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
    
    async def get_user(self, user_id: str) -> Optional[UserResponse]:
        """Get a user by ID."""
        user = await self.repository.get(user_id)
        if not user:
            return None
        return UserResponse.from_orm(user)
    
    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get extended user profile by ID."""
        user = await self.repository.get(user_id)
        if not user:
            return None
        
        # Get additional profile data
        profile_data = UserResponse.from_orm(user).dict()
        profile_data.update({
            "last_login": None,  # TODO: Implement last login tracking
            "login_count": 0,    # TODO: Implement login count tracking
            "created_checklists": 0,  # TODO: Get from safety module
            "approved_checklists": 0  # TODO: Get from safety module
        })
        
        return UserProfile(**profile_data)
    
    async def get_user_by_email(self, email: str) -> Optional[UserResponse]:
        """Get a user by email."""
        user = await self.repository.get_by_email(email)
        if not user:
            return None
        return UserResponse.from_orm(user)
    
    async def list_users(
        self, 
        page: int = 1, 
        per_page: int = 50,
        search: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> UserListResponse:
        """List users with pagination and filtering."""
        if per_page > 100:
            per_page = 100
        
        skip = (page - 1) * per_page
        filters = {}
        
        if search:
            filters["search"] = search
        if role:
            filters["role"] = role
        if is_active is not None:
            filters["is_active"] = is_active
        
        users = await self.repository.list(skip=skip, limit=per_page, filters=filters)
        total = await self.repository.count(filters=filters)
        
        return UserListResponse(
            items=[UserResponse.from_orm(user) for user in users],
            total=total,
            page=page,
            per_page=per_page,
            pages=math.ceil(total / per_page)
        )
    
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user."""
        # Check if email already exists
        existing_user = await self.repository.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        user = await self.repository.create(user_data.dict())
        
        # Publish user created event
        event = UserCreatedEvent(
            user_id=user.id,
            email=user.email,
            role=user.role
        )
        await event.publish()
        
        # Send welcome email (async)
        try:
            await self.mail_service.send_template(
                to=user.email,
                template="welcome",
                data={
                    "name": user.name,
                    "role": user.role
                }
            )
        except Exception as e:
            # Log error but don't fail user creation
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send welcome email to {user.email}: {e}")
        
        return UserResponse.from_orm(user)
    
    async def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[UserResponse]:
        """Update a user."""
        # Check if email is being changed and already exists
        if hasattr(user_data, 'email') and user_data.email:
            existing_user = await self.repository.get_by_email(user_data.email)
            if existing_user and existing_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        user = await self.repository.update(user_id, user_data.dict(exclude_unset=True))
        if not user:
            return None
        
        return UserResponse.from_orm(user)
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete (deactivate) a user."""
        user = await self.repository.deactivate_user(user_id)
        return user is not None
    
    async def change_password(
        self, 
        user_id: str, 
        current_password: str, 
        new_password: str
    ) -> bool:
        """Change a user's password."""
        user = await self.repository.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify current password
        if not await self.repository.verify_password(user, current_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        await self.repository.update(user_id, {"password": new_password})
        return True
    
    async def reset_password_request(self, email: str) -> bool:
        """Request a password reset."""
        user = await self.repository.get_by_email(email)
        if not user or not user.is_active:
            # Don't reveal if email exists
            return True
        
        # Generate reset token (in production, store this in cache/db)
        reset_token = create_access_token(
            {"sub": user.id, "type": "password_reset"},
            expires_delta=timedelta(hours=1)
        )
        
        # Send reset email
        try:
            await self.mail_service.send_template(
                to=user.email,
                template="password_reset",
                data={
                    "name": user.name,
                    "reset_token": reset_token,
                    "reset_url": f"https://app.uehub.com/reset-password?token={reset_token}"
                }
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send password reset email to {user.email}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send reset email"
            )
        
        return True
    
    async def reset_password_confirm(self, token: str, new_password: str) -> bool:
        """Confirm password reset with token."""
        try:
            token_data = verify_token(token)
            
            # Verify it's a password reset token
            if token_data.payload.get("type") != "password_reset":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid reset token"
                )
            
            # Update password
            await self.repository.update(token_data.user_id, {"password": new_password})
            return True
        
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
    
    async def get_users_by_role(self, role: str) -> List[UserResponse]:
        """Get users by role."""
        users = await self.repository.get_users_by_role(role)
        return [UserResponse.from_orm(user) for user in users]