"""
Authentication and authorization utilities.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from .settings import get_settings

settings = get_settings()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token scheme
security = HTTPBearer()


class TokenData(BaseModel):
    """JWT token data."""
    user_id: str
    email: str
    role: str
    exp: datetime


class CurrentUser(BaseModel):
    """Current authenticated user."""
    id: str
    email: str
    name: str
    role: str


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.auth.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.auth.secret_key, 
        algorithm=settings.auth.algorithm
    )
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.auth.refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.auth.secret_key,
        algorithm=settings.auth.algorithm
    )
    return encoded_jwt


def verify_token(token: str) -> TokenData:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(
            token, 
            settings.auth.secret_key, 
            algorithms=[settings.auth.algorithm]
        )
        
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        role: str = payload.get("role")
        exp: float = payload.get("exp")
        
        if user_id is None or email is None or role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return TokenData(
            user_id=user_id,
            email=email,
            role=role,
            exp=datetime.fromtimestamp(exp)
        )
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> CurrentUser:
    """Get the current authenticated user."""
    token_data = verify_token(credentials.credentials)
    
    # In a real app, you'd fetch the user from the database here
    # For now, we'll construct it from the token data
    return CurrentUser(
        id=token_data.user_id,
        email=token_data.email,
        name=token_data.email.split("@")[0],  # Simple name extraction
        role=token_data.role
    )


def require_role(required_role: str):
    """Decorator to require a specific role."""
    def role_checker(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires {required_role} role"
            )
        return current_user
    return role_checker


def require_roles(*required_roles: str):
    """Decorator to require one of multiple roles."""
    def role_checker(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if current_user.role not in required_roles:
            roles_str = ", ".join(required_roles)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires one of: {roles_str}"
            )
        return current_user
    return role_checker


# Role-based dependencies
def require_admin(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """Require admin role."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def require_manager_or_admin(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """Require manager or admin role."""
    if current_user.role not in ["manager", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager or admin access required"
        )
    return current_user


def require_authenticated(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """Require any authenticated user."""
    return current_user


# Permission system
class Permission:
    """Permission constants."""
    
    # User management
    CREATE_USER = "user:create"
    UPDATE_USER = "user:update"
    DELETE_USER = "user:delete"
    VIEW_USER = "user:view"
    
    # Inventory management
    CREATE_INVENTORY = "inventory:create"
    UPDATE_INVENTORY = "inventory:update"
    DELETE_INVENTORY = "inventory:delete"
    VIEW_INVENTORY = "inventory:view"
    
    # Training management
    CREATE_TRAINING = "training:create"
    UPDATE_TRAINING = "training:update"
    DELETE_TRAINING = "training:delete"
    VIEW_TRAINING = "training:view"
    TAKE_TRAINING = "training:take"
    
    # Certificate management
    VIEW_CERTIFICATE = "certificate:view"
    ISSUE_CERTIFICATE = "certificate:issue"
    
    # Reporting
    VIEW_REPORTS = "reports:view"
    CREATE_REPORTS = "reports:create"
    
    # Webhook management
    CREATE_WEBHOOK = "webhook:create"
    UPDATE_WEBHOOK = "webhook:update"
    DELETE_WEBHOOK = "webhook:delete"
    VIEW_WEBHOOK = "webhook:view"


# Role permissions mapping
ROLE_PERMISSIONS = {
    "admin": [
        # All permissions
        Permission.CREATE_USER,
        Permission.UPDATE_USER,
        Permission.DELETE_USER,
        Permission.VIEW_USER,
        Permission.CREATE_INVENTORY,
        Permission.UPDATE_INVENTORY,
        Permission.DELETE_INVENTORY,
        Permission.VIEW_INVENTORY,
        Permission.CREATE_TRAINING,
        Permission.UPDATE_TRAINING,
        Permission.DELETE_TRAINING,
        Permission.VIEW_TRAINING,
        Permission.TAKE_TRAINING,
        Permission.VIEW_CERTIFICATE,
        Permission.ISSUE_CERTIFICATE,
        Permission.VIEW_REPORTS,
        Permission.CREATE_REPORTS,
        Permission.CREATE_WEBHOOK,
        Permission.UPDATE_WEBHOOK,
        Permission.DELETE_WEBHOOK,
        Permission.VIEW_WEBHOOK,
    ],
    "manager": [
        Permission.VIEW_USER,
        Permission.CREATE_INVENTORY,
        Permission.UPDATE_INVENTORY,
        Permission.VIEW_INVENTORY,
        Permission.CREATE_TRAINING,
        Permission.UPDATE_TRAINING,
        Permission.VIEW_TRAINING,
        Permission.TAKE_TRAINING,
        Permission.VIEW_CERTIFICATE,
        Permission.ISSUE_CERTIFICATE,
        Permission.VIEW_REPORTS,
        Permission.CREATE_REPORTS,
        Permission.VIEW_WEBHOOK,
    ],
    "worker": [
        Permission.VIEW_INVENTORY,
        Permission.VIEW_TRAINING,
        Permission.TAKE_TRAINING,
        Permission.VIEW_CERTIFICATE,
    ],
}


def has_permission(user_role: str, permission: str) -> bool:
    """Check if a role has a specific permission."""
    return permission in ROLE_PERMISSIONS.get(user_role, [])


def require_permission(permission: str):
    """Decorator to require a specific permission."""
    def permission_checker(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if not has_permission(current_user.role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission required: {permission}"
            )
        return current_user
    return permission_checker
