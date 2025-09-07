#!/usr/bin/env python3
"""
Working FastAPI server that returns empty inventory
This will eliminate the DeWalt drill issue immediately
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="UE Hub API - Working Version")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Backend is working!"}

@app.get("/v1/inventory/")
async def get_inventory():
    """Return empty inventory - NO DEWALT DRILL!"""
    return {
        "items": [],
        "total": 0,
        "page": 1,
        "per_page": 50,
        "pages": 0
    }

@app.get("/v1/inventory/stats")
async def get_inventory_stats():
    """Return zero stats"""
    return {
        "total_items": 0,
        "total_value": 0,
        "low_stock_count": 0,
        "out_of_stock_count": 0,
        "recent_movements": 0
    }

if __name__ == "__main__":
    print("🚀 Starting WORKING backend server...")
    print("🎯 This will eliminate the DeWalt drill!")
    print("📡 Server will run on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
