#!/usr/bin/env python3
"""
Simple working backend server for inventory.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="UE Hub Simple Backend")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Simple backend working"}

@app.get("/v1/inventory/")
async def get_inventory():
    """Get inventory items - returns empty list since database is empty."""
    return {
        "items": [],
        "total": 0,
        "page": 1,
        "per_page": 50,
        "pages": 0
    }

@app.get("/v1/inventory/stats")
async def get_stats():
    """Get inventory stats - returns zeros since database is empty."""
    return {
        "total_items": 0,
        "total_value": 0,
        "low_stock_count": 0,
        "out_of_stock_count": 0,
        "recent_movements": 0
    }

@app.post("/v1/inventory/")
async def create_item(item: dict):
    """Create inventory item - placeholder."""
    return {"message": "Item creation not implemented yet"}

@app.put("/v1/inventory/{item_id}")
async def update_item(item_id: str, item: dict):
    """Update inventory item - placeholder."""
    return {"message": "Item update not implemented yet"}

@app.delete("/v1/inventory/{item_id}")
async def delete_item(item_id: str):
    """Delete inventory item - placeholder."""
    return {"message": "Item deletion not implemented yet"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Simple UE Hub Backend...")
    print("📊 Will return empty inventory (0 items)")
    print("🔗 Available at: http://localhost:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
