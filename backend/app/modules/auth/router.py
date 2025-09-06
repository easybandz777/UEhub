"""
Authentication module router.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.container import get_event_bus_dep, get_mail_service
from ...core.db import get_db
from ...core.interfaces import EventBus, MailService
from ...core.security import (
    CurrentUser,
    require_admin,
    require_authenticated,
    require_manager_or_admin,
)
from .repository import AuthRepository
from .schemas import (
    ChangePasswordRequest,
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    ResetPasswordConfirm,
    ResetPasswordRequest,
    UserCreate,
    UserListResponse,
    UserResponse,
    UserUpdate,
)
from .service import AuthService

router = APIRouter()


def get_auth_service(
    db: AsyncSession = Depends(get_db),
    event_bus: EventBus = Depends(get_event_bus_dep),
    mail_service: MailService = Depends(get_mail_service)
) -> AuthService:
    """Get auth service with dependencies."""
    repository = AuthRepository(db)
    return AuthService(repository, event_bus, mail_service)


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Login with email and password."""
    return await auth_service.login(login_data.email, login_data.password)


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Refresh access token."""
    return await auth_service.refresh_token(refresh_data.refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: CurrentUser = Depends(require_authenticated),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Get current user information."""
    user = await auth_service.get_user(current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: CurrentUser = Depends(require_authenticated),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Change current user's password."""
    await auth_service.change_password(
        current_user.id,
        password_data.current_password,
        password_data.new_password
    )
    return {"message": "Password changed successfully"}


@router.post("/reset-password")
async def reset_password_request(
    reset_data: ResetPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Request password reset."""
    await auth_service.reset_password_request(reset_data.email)
    return {"message": "If the email exists, a reset link has been sent"}


@router.post("/reset-password/confirm")
async def reset_password_confirm(
    reset_data: ResetPasswordConfirm,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Confirm password reset."""
    await auth_service.reset_password_confirm(reset_data.token, reset_data.new_password)
    return {"message": "Password reset successfully"}


# Admin endpoints
@router.get("/users", response_model=UserListResponse)
async def list_users(
    page: int = 1,
    per_page: int = 50,
    search: str = None,
    role: str = None,
    is_active: bool = None,
    current_user: CurrentUser = Depends(require_manager_or_admin),
    auth_service: AuthService = Depends(get_auth_service)
):
    """List users (admin/manager only)."""
    return await auth_service.list_users(
        page=page,
        per_page=per_page,
        search=search,
        role=role,
        is_active=is_active
    )


@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: CurrentUser = Depends(require_admin),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Create a new user (admin only)."""
    return await auth_service.create_user(user_data)


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: CurrentUser = Depends(require_manager_or_admin),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Get user by ID (admin/manager only)."""
    user = await auth_service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: CurrentUser = Depends(require_admin),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Update user (admin only)."""
    user = await auth_service.update_user(user_id, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: CurrentUser = Depends(require_admin),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Delete (deactivate) user (admin only)."""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    success = await auth_service.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "User deleted successfully"}


@router.get("/users/role/{role}", response_model=list[UserResponse])
async def get_users_by_role(
    role: str,
    current_user: CurrentUser = Depends(require_manager_or_admin),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Get users by role (admin/manager only)."""
    return await auth_service.get_users_by_role(role)
