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
    require_superadmin,
    require_admin_or_superadmin,
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
    UserRegister,
    UserListResponse,
    UserResponse,
    UserUpdate,
    UserProfile,
    RolePermissions,
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


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserRegister,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Register a new user (public endpoint - creates employee by default)."""
    # Convert to UserCreate with employee role
    user_create_data = UserCreate(
        email=user_data.email,
        name=user_data.name,
        password=user_data.password,
        role="employee"  # Default role for public registration
    )
    return await auth_service.create_user(user_create_data)


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


@router.get("/me", response_model=UserProfile)
async def get_current_user_info(
    current_user: CurrentUser = Depends(require_authenticated),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Get current user information."""
    user = await auth_service.get_user_profile(current_user.id)
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


@router.get("/roles", response_model=list[RolePermissions])
async def get_role_permissions(
    current_user: CurrentUser = Depends(require_authenticated)
):
    """Get role permissions information."""
    roles = [
        RolePermissions(
            role="superadmin",
            permissions=[
                "manage_users", "manage_roles", "view_all_checklists", 
                "approve_checklists", "manage_templates", "system_admin"
            ],
            description="Full system access and user management"
        ),
        RolePermissions(
            role="admin",
            permissions=[
                "view_all_checklists", "approve_checklists", 
                "manage_templates", "view_users"
            ],
            description="Checklist approval and template management"
        ),
        RolePermissions(
            role="employee",
            permissions=[
                "create_checklists", "view_own_checklists", "edit_own_checklists"
            ],
            description="Create and manage own safety checklists"
        )
    ]
    return roles


# Admin endpoints
@router.get("/users", response_model=UserListResponse)
async def list_users(
    page: int = 1,
    per_page: int = 50,
    search: str = None,
    role: str = None,
    is_active: bool = None,
    current_user: CurrentUser = Depends(require_admin_or_superadmin),
    auth_service: AuthService = Depends(get_auth_service)
):
    """List users (admin/superadmin only)."""
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
    current_user: CurrentUser = Depends(require_superadmin),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Create a new user (superadmin only)."""
    return await auth_service.create_user(user_data)


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: CurrentUser = Depends(require_admin_or_superadmin),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Get user by ID (admin/superadmin only)."""
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
    current_user: CurrentUser = Depends(require_superadmin),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Update user (superadmin only)."""
    user = await auth_service.update_user(user_id, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/users/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: str,
    role_data: dict,
    current_user: CurrentUser = Depends(require_superadmin),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Update user role (superadmin only)."""
    if "role" not in role_data or role_data["role"] not in ["superadmin", "admin", "employee"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be superadmin, admin, or employee"
        )
    
    user_update = UserUpdate(role=role_data["role"])
    user = await auth_service.update_user(user_id, user_update)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: CurrentUser = Depends(require_superadmin),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Delete (deactivate) user (superadmin only)."""
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
    current_user: CurrentUser = Depends(require_admin_or_superadmin),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Get users by role (admin/superadmin only)."""
    return await auth_service.get_users_by_role(role)