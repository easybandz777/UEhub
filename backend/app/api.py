"""
Main FastAPI application.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from .core.health import router as health_router
from .core.settings import get_settings
from .core.sentry import init_sentry
from .core.security import get_current_user
from .modules.auth.router import router as auth_router
from .modules.inventory.router import router as inventory_router
from .modules.safety.router import router as safety_router
from .modules.timeclock.router import router as timeclock_router
from .test_router import test_router

# Import other module routers as they're created
# from .modules.training.router import router as training_router
# from .modules.certs.router import router as certs_router
# from .modules.reporting.router import router as reporting_router
# from .modules.webhooks.router import router as webhooks_router

settings = get_settings()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.app.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Initialize Sentry for error tracking
# init_sentry()  # Temporarily disabled to fix startup issue


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logging.info(f"Starting UE Hub API v{settings.app.version}")
    logging.info(f"Environment: {settings.app.environment}")
    
    # Initialize event bus and register handlers
    from .core.container import get_container
    container = get_container()
    
    # Register event handlers here
    # await register_event_handlers(container.event_bus)
    
    yield
    
    # Shutdown
    logging.info("Shutting down UE Hub API")
    
    # Close event bus connections
    if hasattr(container.event_bus, 'close'):
        await container.event_bus.close()


# Create FastAPI app
app = FastAPI(
    title=settings.app.name,
    description=settings.app.description,
    version=settings.app.version,
    docs_url="/docs" if settings.app.enable_docs else None,
    redoc_url="/redoc" if settings.app.enable_docs else None,
    openapi_url="/openapi.json" if settings.app.enable_docs else None,
    lifespan=lifespan,
)

# Add middleware
# Debug CORS origins
logging.info(f"CORS origins configured: {settings.app.cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Explicitly allow all origins
    allow_credentials=False,  # Set to False when using "*" for origins
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.app.allowed_hosts,
)

# Test endpoint to debug authentication issues
@app.get("/test-no-auth")
async def test_no_auth():
    """Test endpoint with no authentication."""
    return {"message": "This endpoint works without auth", "status": "success"}

@app.get("/test-db")
async def test_db():
    """Test database connection."""
    try:
        from .core.db import get_db
        from .modules.auth.repository import AuthRepository
        
        async for db in get_db():
            repo = AuthRepository(db)
            user = await repo.get_by_email('admin@uehub.com')
            
            if user:
                # Test password verification
                password_valid = await repo.verify_password(user, 'Admin123!@#')
                
                return {
                    "status": "success",
                    "message": "Database connection working",
                    "user_found": True,
                    "user_email": user.email,
                    "user_role": user.role,
                    "user_active": user.is_active,
                    "password_valid": password_valid
                }
            else:
                return {
                    "status": "error",
                    "message": "Database connected but admin user not found",
                    "user_found": False
                }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": f"Database connection failed: {str(e)}",
            "user_found": False,
            "traceback": traceback.format_exc()
        }

@app.post("/test-auth")
async def test_auth():
    """Test authentication without dependencies."""
    try:
        from .core.db import get_db
        from .modules.auth.repository import AuthRepository
        from .core.security import create_access_token, create_refresh_token
        
        async for db in get_db():
            repo = AuthRepository(db)
            user = await repo.get_by_email('admin@uehub.com')
            
            if user and user.is_active:
                password_valid = await repo.verify_password(user, 'Admin123!@#')
                
                if password_valid:
                    # Create tokens directly
                    token_data = {
                        "sub": user.id,
                        "email": user.email,
                        "role": user.role
                    }
                    
                    access_token = create_access_token(token_data)
                    refresh_token = create_refresh_token(token_data)
                    
                    return {
                        "status": "success",
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "token_type": "bearer",
                        "expires_in": 1800,
                        "user": {
                            "id": user.id,
                            "email": user.email,
                            "name": user.name,
                            "role": user.role,
                            "is_active": user.is_active
                        }
                    }
                else:
                    return {"status": "error", "message": "Invalid password"}
            else:
                return {"status": "error", "message": "User not found or inactive"}
                
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": f"Auth test failed: {str(e)}",
            "traceback": traceback.format_exc()
        }

# TEMPORARY DASHBOARD ENDPOINT - Returns mock data until safety tables are created
@app.get("/v1/safety/dashboard")
async def temporary_dashboard():
    """Temporary dashboard endpoint with mock data."""
    return {
        "stats": {
            "total_checklists": 0,
            "completed_checklists": 0,
            "approved_checklists": 0,
            "pending_approval": 0,
            "critical_failures_count": 0,
            "average_completion_rate": 0.0,
            "checklists_this_month": 0,
            "checklists_this_week": 0
        },
        "recent_checklists": [],
        "pending_approvals": [],
        "critical_failures": [],
        "completion_trend": []
    }

    # TEMPORARY INVENTORY ENDPOINTS - Bypass SQLAlchemy ORM issues with raw SQL
    @app.get("/v1/inventory")
    @app.get("/v1/inventory/")
    async def temporary_inventory_list(current_user = Depends(get_current_user)):
        """Temporary inventory list endpoint using raw SQL with user filtering."""
        try:
            from .core.db import get_db
            from sqlalchemy import text
            
            async for db in get_db():
                # Admin users can see all inventory, others see only their own
                if current_user.role == "admin":
                    # Admin sees all inventory with user information
                    result = await db.execute(
                        text("""
                            SELECT i.id, i.sku, i.name, i.location, i.barcode, i.qty, i.min_qty, 
                                   i.created_at, i.updated_at, i.user_id, u.name as user_name, u.email as user_email
                            FROM inventory_items i 
                            LEFT JOIN auth_user u ON i.user_id = u.id 
                            ORDER BY i.created_at DESC
                        """)
                    )
                else:
                    # Regular users see only their own inventory
                    result = await db.execute(
                        text("""
                            SELECT id, sku, name, location, barcode, qty, min_qty, created_at, updated_at, user_id
                            FROM inventory_items 
                            WHERE user_id = :user_id 
                            ORDER BY created_at DESC
                        """),
                        {"user_id": current_user.id}
                    )
                rows = result.fetchall()
                
                items = []
                for row in rows:
                    item_data = {
                        "id": str(row.id),
                        "sku": row.sku,
                        "name": row.name,
                        "location": row.location,
                        "barcode": row.barcode,
                        "qty": row.qty,
                        "min_qty": row.min_qty,
                        "is_low_stock": row.qty <= row.min_qty,
                        "updated_at": row.updated_at.isoformat() if row.updated_at else None,
                        "user_id": row.user_id
                    }
                    if current_user.role == "admin":
                        item_data["user_name"] = row.user_name
                        item_data["user_email"] = row.user_email
                    items.append(item_data)
                
                return {
                    "items": items,
                    "total": len(items),
                    "page": 1,
                    "per_page": 50,
                    "pages": 1
                }
                
        except Exception as e:
            import traceback
            return {
                "items": [],
                "total": 0,
                "page": 1,
                "per_page": 50,
                "pages": 1,
                "error": f"Failed to load inventory: {str(e)}",
                "traceback": traceback.format_exc()
            }

@app.post("/v1/inventory")
@app.post("/v1/inventory/")
async def temporary_inventory_create(item_data: dict, current_user = Depends(get_current_user)):
    """Temporary inventory creation endpoint using raw SQL."""
    try:
        from .core.db import get_db
        from sqlalchemy import text
        import uuid
        
        user_id = current_user.id
        
        async for db in get_db():
            # Generate UUID for new item
            item_id = str(uuid.uuid4())
            
            # Insert new inventory item using raw SQL with user_id
            await db.execute(
                text("""
                    INSERT INTO inventory_items (id, sku, name, location, barcode, qty, min_qty, user_id, created_at, updated_at)
                    VALUES (:id, :sku, :name, :location, :barcode, :qty, :min_qty, :user_id, NOW(), NOW())
                """),
                {
                    "id": item_id,
                    "sku": item_data.get("sku", ""),
                    "name": item_data.get("name", ""),
                    "location": item_data.get("location", ""),
                    "barcode": item_data.get("barcode"),
                    "qty": item_data.get("qty", 0),
                    "min_qty": item_data.get("min_qty", 0),
                    "user_id": user_id
                }
            )
            
            # Commit the transaction
            await db.commit()
            
            # Return the created item
            return {
                "id": item_id,
                "sku": item_data.get("sku", ""),
                "name": item_data.get("name", ""),
                "location": item_data.get("location", ""),
                "barcode": item_data.get("barcode"),
                "qty": item_data.get("qty", 0),
                "min_qty": item_data.get("min_qty", 0),
                "is_low_stock": item_data.get("qty", 0) <= item_data.get("min_qty", 0),
                "created_at": None,  # Will be set by database
                "updated_at": None   # Will be set by database
            }
            
    except Exception as e:
        import traceback
        return {
            "error": f"Failed to create inventory item: {str(e)}",
            "traceback": traceback.format_exc()
        }

# USER MANAGEMENT ENDPOINTS - For super admin only
@app.get("/v1/admin/test")
async def test_admin_endpoint():
    """Test endpoint to verify admin routes are working."""
    return {"message": "Admin endpoints are working!", "status": "success"}

@app.get("/v1/admin/users")
async def get_all_users():
    """Get all users - Super admin only."""
    try:
        from .core.db import get_db
        from sqlalchemy import text
        
        # TODO: Add super admin role check
        # For now, return all users
        
        async for db in get_db():
            result = await db.execute(
                text("""
                    SELECT id, email, name, role, is_active, created_at, updated_at, 
                           phone, department, notes
                    FROM auth_user 
                    ORDER BY created_at DESC
                """)
            )
            rows = result.fetchall()
            
            users = []
            for row in rows:
                users.append({
                    "id": row.id,
                    "email": row.email,
                    "name": row.name,
                    "role": row.role,
                    "is_active": row.is_active,
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                    "updated_at": row.updated_at.isoformat() if row.updated_at else None,
                    "phone": row.phone,
                    "department": row.department,
                    "notes": row.notes
                })
            
            return {
                "users": users,
                "total": len(users)
            }
            
    except Exception as e:
        import traceback
        return {
            "users": [],
            "total": 0,
            "error": f"Failed to load users: {str(e)}",
            "traceback": traceback.format_exc()
        }

@app.post("/v1/admin/users")
async def create_user(user_data: dict):
    """Create a new user - Super admin only."""
    try:
        from .core.db import get_db
        from sqlalchemy import text
        from passlib.context import CryptContext
        import uuid
        
        # TODO: Add super admin role check
        
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        async for db in get_db():
            # Check if email already exists
            existing_result = await db.execute(
                text("SELECT id FROM auth_user WHERE email = :email"),
                {"email": user_data.get("email")}
            )
            if existing_result.fetchone():
                return {"error": "Email already exists"}
            
            # Generate UUID for new user
            user_id = str(uuid.uuid4())
            
            # Hash password
            hashed_password = pwd_context.hash(user_data.get("password", "DefaultPass123!"))
            
            # Insert new user
            await db.execute(
                text("""
                    INSERT INTO auth_user (id, email, name, password_hash, role, is_active, 
                                         phone, department, notes, created_at, updated_at)
                    VALUES (:id, :email, :name, :password_hash, :role, :is_active, 
                           :phone, :department, :notes, NOW(), NOW())
                """),
                {
                    "id": user_id,
                    "email": user_data.get("email"),
                    "name": user_data.get("name"),
                    "password_hash": hashed_password,
                    "role": user_data.get("role", "employee"),
                    "is_active": user_data.get("is_active", True),
                    "phone": user_data.get("phone"),
                    "department": user_data.get("department"),
                    "notes": user_data.get("notes")
                }
            )
            
            await db.commit()
            
            return {
                "id": user_id,
                "email": user_data.get("email"),
                "name": user_data.get("name"),
                "role": user_data.get("role", "employee"),
                "is_active": user_data.get("is_active", True),
                "phone": user_data.get("phone"),
                "department": user_data.get("department"),
                "notes": user_data.get("notes"),
                "message": "User created successfully"
            }
            
    except Exception as e:
        import traceback
        return {
            "error": f"Failed to create user: {str(e)}",
            "traceback": traceback.format_exc()
        }

@app.put("/v1/admin/users/{user_id}")
async def update_user(user_id: str, user_data: dict):
    """Update a user - Super admin only."""
    try:
        from .core.db import get_db
        from sqlalchemy import text
        from passlib.context import CryptContext
        
        # TODO: Add super admin role check
        
        async for db in get_db():
            # Check if user exists
            existing_result = await db.execute(
                text("SELECT id FROM auth_user WHERE id = :user_id"),
                {"user_id": user_id}
            )
            if not existing_result.fetchone():
                return {"error": "User not found"}
            
            # Build update query dynamically
            update_fields = []
            params = {"user_id": user_id}
            
            if "name" in user_data:
                update_fields.append("name = :name")
                params["name"] = user_data["name"]
            
            if "email" in user_data:
                update_fields.append("email = :email")
                params["email"] = user_data["email"]
            
            if "role" in user_data:
                update_fields.append("role = :role")
                params["role"] = user_data["role"]
            
            if "is_active" in user_data:
                update_fields.append("is_active = :is_active")
                params["is_active"] = user_data["is_active"]
            
            if "phone" in user_data:
                update_fields.append("phone = :phone")
                params["phone"] = user_data["phone"]
            
            if "department" in user_data:
                update_fields.append("department = :department")
                params["department"] = user_data["department"]
            
            if "notes" in user_data:
                update_fields.append("notes = :notes")
                params["notes"] = user_data["notes"]
            
            if "password" in user_data:
                pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
                hashed_password = pwd_context.hash(user_data["password"])
                update_fields.append("password_hash = :password_hash")
                params["password_hash"] = hashed_password
            
            if update_fields:
                update_fields.append("updated_at = NOW()")
                query = f"UPDATE auth_user SET {', '.join(update_fields)} WHERE id = :user_id"
                
                await db.execute(text(query), params)
                await db.commit()
            
            return {"message": "User updated successfully"}
            
    except Exception as e:
        import traceback
        return {
            "error": f"Failed to update user: {str(e)}",
            "traceback": traceback.format_exc()
        }

@app.delete("/v1/admin/users/{user_id}")
async def delete_user(user_id: str):
    """Delete a user - Super admin only."""
    try:
        from .core.db import get_db
        from sqlalchemy import text
        
        # TODO: Add super admin role check
        
        async for db in get_db():
            # Check if user exists
            existing_result = await db.execute(
                text("SELECT id FROM auth_user WHERE id = :user_id"),
                {"user_id": user_id}
            )
            if not existing_result.fetchone():
                return {"error": "User not found"}
            
            # Soft delete - set is_active to false
            await db.execute(
                text("UPDATE auth_user SET is_active = false, updated_at = NOW() WHERE id = :user_id"),
                {"user_id": user_id}
            )
            await db.commit()
            
            return {"message": "User deactivated successfully"}
            
    except Exception as e:
        import traceback
        return {
            "error": f"Failed to delete user: {str(e)}",
            "traceback": traceback.format_exc()
        }

@app.get("/v1/admin/users/{user_id}/inventory")
async def get_user_inventory(user_id: str):
    """Get inventory for a specific user - Super admin only."""
    try:
        from .core.db import get_db
        from sqlalchemy import text
        
        # TODO: Add super admin role check
        
        async for db in get_db():
            # Get user info
            user_result = await db.execute(
                text("SELECT name, email FROM auth_user WHERE id = :user_id"),
                {"user_id": user_id}
            )
            user_row = user_result.fetchone()
            if not user_row:
                return {"error": "User not found"}
            
            # Get user's inventory
            inventory_result = await db.execute(
                text("""
                    SELECT id, sku, name, location, barcode, qty, min_qty, created_at, updated_at
                    FROM inventory_items 
                    WHERE user_id = :user_id 
                    ORDER BY created_at DESC
                """),
                {"user_id": user_id}
            )
            rows = inventory_result.fetchall()
            
            items = []
            for row in rows:
                items.append({
                    "id": str(row.id),
                    "sku": row.sku,
                    "name": row.name,
                    "location": row.location,
                    "barcode": row.barcode,
                    "qty": row.qty,
                    "min_qty": row.min_qty,
                    "is_low_stock": row.qty <= row.min_qty,
                    "updated_at": row.updated_at.isoformat() if row.updated_at else None
                })
            
            return {
                "user": {
                    "id": user_id,
                    "name": user_row.name,
                    "email": user_row.email
                },
                "inventory": {
                    "items": items,
                    "total": len(items)
                }
            }
            
    except Exception as e:
        import traceback
        return {
            "error": f"Failed to load user inventory: {str(e)}",
            "traceback": traceback.format_exc()
        }

@app.get("/v1/inventory/stats")
async def temporary_inventory_stats():
    """Temporary inventory stats endpoint using raw SQL."""
    try:
        from .core.db import get_db
        from sqlalchemy import text
        
        async for db in get_db():
            # Raw SQL queries for stats
            total_result = await db.execute(text("SELECT COUNT(*) as count FROM inventory_items"))
            total_items = total_result.fetchone().count
            
            low_stock_result = await db.execute(text("SELECT COUNT(*) as count FROM inventory_items WHERE qty <= min_qty"))
            low_stock_count = low_stock_result.fetchone().count
            
            out_of_stock_result = await db.execute(text("SELECT COUNT(*) as count FROM inventory_items WHERE qty = 0"))
            out_of_stock_count = out_of_stock_result.fetchone().count
            
            # Calculate total value (assuming no price field, use qty as placeholder)
            value_result = await db.execute(text("SELECT SUM(qty) as total FROM inventory_items"))
            total_value = value_result.fetchone().total or 0
            
            return {
                "total_items": total_items,
                "total_value": float(total_value),  # Placeholder calculation
                "low_stock_count": low_stock_count,
                "out_of_stock_count": out_of_stock_count,
                "recent_movements": 0  # No movements table data yet
            }
            
    except Exception as e:
        import traceback
        return {
            "total_items": 0,
            "total_value": 0.0,
            "low_stock_count": 0,
            "out_of_stock_count": 0,
            "recent_movements": 0,
            "error": f"Failed to load stats: {str(e)}",
            "traceback": traceback.format_exc()
        }

# EMERGENCY LOGIN ENDPOINT - Bypasses all dependencies
@app.post("/emergency-login")
async def emergency_login(login_data: dict):
    """Emergency login endpoint that bypasses all complex dependencies."""
    try:
        email = login_data.get("email")
        password = login_data.get("password")
        
        if not email or not password:
            return {"error": "Email and password required"}, 400
        
        from .core.db import get_db
        from .modules.auth.repository import AuthRepository
        from .core.security import create_access_token, create_refresh_token
        
        async for db in get_db():
            repo = AuthRepository(db)
            user = await repo.get_by_email(email)
            
            if user and user.is_active:
                password_valid = await repo.verify_password(user, password)
                
                if password_valid:
                    # Create tokens directly
                    token_data = {
                        "sub": user.id,
                        "email": user.email,
                        "role": user.role
                    }
                    
                    access_token = create_access_token(token_data)
                    refresh_token = create_refresh_token(token_data)
                    
                    return {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "token_type": "bearer",
                        "expires_in": 1800,
                        "user": {
                            "id": user.id,
                            "email": user.email,
                            "name": user.name,
                            "role": user.role,
                            "is_active": user.is_active,
                            "created_at": user.created_at.isoformat(),
                            "updated_at": user.updated_at.isoformat()
                        }
                    }
                else:
                    return {"detail": "Invalid email or password"}, 401
            else:
                return {"detail": "Invalid email or password"}, 401
                
    except Exception as e:
        import traceback
        return {
            "detail": f"Login failed: {str(e)}",
            "traceback": traceback.format_exc()
        }, 500

# NUCLEAR TEST - Direct inventory endpoint outside /v1/ prefix
@app.get("/direct-inventory-test")
async def direct_inventory_test():
    """Direct inventory test bypassing all middleware."""
    return {
        "message": "Direct inventory test",
        "items": [],
        "total": 0,
        "status": "working"
    }

# Include routers
app.include_router(health_router, tags=["health"])
app.include_router(auth_router, prefix=f"{settings.app.api_prefix}/auth", tags=["auth"])
# app.include_router(inventory_router, prefix=f"{settings.app.api_prefix}/inventory", tags=["inventory"])  # Disabled - using temporary endpoints
app.include_router(safety_router, prefix=f"{settings.app.api_prefix}/safety", tags=["safety"])
app.include_router(timeclock_router, prefix=f"{settings.app.api_prefix}/timeclock", tags=["timeclock"])

# NUCLEAR TEST ROUTER - NO DEPENDENCIES
app.include_router(test_router, prefix="/nuclear", tags=["nuclear-test"])

# Include other module routers as they're created
# app.include_router(training_router, prefix=f"{settings.app.api_prefix}/training", tags=["training"])
# app.include_router(certs_router, prefix=f"{settings.app.api_prefix}/certs", tags=["certificates"])
# app.include_router(reporting_router, prefix=f"{settings.app.api_prefix}/reports", tags=["reporting"])
# app.include_router(webhooks_router, prefix=f"{settings.app.api_prefix}/webhooks", tags=["webhooks"])


@app.options("/{path:path}")
async def options_handler(path: str):
    """Handle OPTIONS requests for CORS preflight."""
    return {"message": "OK"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app.name,
        "version": settings.app.version,
        "environment": settings.app.environment,
        "docs_url": "/docs" if settings.app.enable_docs else None,
    }


@app.get("/info")
async def info():
    """Application information."""
    return {
        "name": settings.app.name,
        "description": settings.app.description,
        "version": settings.app.version,
        "environment": settings.app.environment,
        "api_prefix": settings.app.api_prefix,
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler."""
    return {
        "detail": "The requested resource was not found",
        "status_code": 404,
        "path": str(request.url.path),
    }


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Custom 500 handler."""
    logging.error(f"Internal server error: {exc}")
    return {
        "detail": "An internal server error occurred",
        "status_code": 500,
    }


# Feature flag middleware
@app.middleware("http")
async def feature_flag_middleware(request, call_next):
    """Check feature flags for protected routes."""
    from .core.container import get_container
    
    # Get feature flags (in production, cache these)
    try:
        container = get_container()
        # feature_flags = await get_feature_flags()  # Implement this
        
        # Check if route is protected by feature flags
        path = request.url.path
        
        # Example feature flag checks
        if path.startswith("/v1/reports") and not True:  # Replace with actual flag check
            return {"detail": "Reporting feature is disabled", "status_code": 404}
        
        if path.startswith("/v1/webhooks") and not True:  # Replace with actual flag check
            return {"detail": "Webhooks feature is disabled", "status_code": 404}
    
    except Exception as e:
        logging.error(f"Feature flag middleware error: {e}")
        # Continue on error to avoid breaking the app
    
    response = await call_next(request)
    return response


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.api:app",
        host="0.0.0.0",
        port=8080,
        reload=settings.app.environment == "development",
        log_level=settings.app.log_level.lower(),
    )