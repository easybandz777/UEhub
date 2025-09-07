"""
NUCLEAR TEST ROUTER - NO DEPENDENCIES AT ALL
"""
from fastapi import APIRouter

# Create router with NO dependencies
test_router = APIRouter()

@test_router.get("/nuclear-test")
def nuclear_test():
    """Absolutely no dependencies test endpoint."""
    return {"message": "NUCLEAR TEST WORKS", "status": "success"}

@test_router.get("/test-inventory")  
def test_inventory():
    """Test inventory without any dependencies."""
    return {
        "items": [],
        "total": 0,
        "message": "This works without auth"
    }

@test_router.post("/test-create")
def test_create():
    """Test create without dependencies.""" 
    return {"message": "Create works", "id": "test-123"}
