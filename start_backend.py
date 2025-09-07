#!/usr/bin/env python3
"""
Start the backend server and test it.
"""
import subprocess
import time
import requests
import sys
import os

def start_backend():
    """Start the backend server."""
    print("🚀 Starting backend server...")
    
    # Change to backend directory
    backend_dir = os.path.join(os.getcwd(), "backend")
    if not os.path.exists(backend_dir):
        print("❌ Backend directory not found!")
        return False
    
    os.chdir(backend_dir)
    
    try:
        # Start the server
        process = subprocess.Popen([
            "py", "-m", "uvicorn", "app.api:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("⏳ Waiting for server to start...")
        time.sleep(5)
        
        # Test if server is responding
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Backend server is running!")
                print(f"📊 Health check response: {response.json()}")
                return True
            else:
                print(f"❌ Server responded with status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Server not responding: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False

if __name__ == "__main__":
    if start_backend():
        print("🎉 Backend is ready!")
        print("🔗 Try: http://localhost:8000/health")
        print("📋 API docs: http://localhost:8000/docs")
    else:
        print("💥 Failed to start backend!")
        sys.exit(1)
