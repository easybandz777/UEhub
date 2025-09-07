#!/usr/bin/env python3
"""
Start backend in development mode with minimal config.
"""
import os
import subprocess
import sys

# Set minimal environment variables
os.environ.update({
    'APP_NAME': 'UE Hub',
    'ENVIRONMENT': 'development',
    'SECRET_KEY': 'development-secret-key-minimum-32-characters-long-for-local-dev',
    'DATABASE_URL': 'postgresql+asyncpg://neondb_owner:npg_EoVzn0WyqX1v@ep-odd-tree-adxsa81s-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require',
    'CORS_ORIGINS': 'http://localhost:3000,http://localhost:3001',
    'ENABLE_DOCS': 'true',
    'LOG_LEVEL': 'INFO'
})

print("🚀 Starting UE Hub Backend...")
print("📊 Environment variables set")
print("🔗 Will be available at: http://localhost:8080")
print("📋 API docs at: http://localhost:8080/docs")

try:
    # Start uvicorn
    subprocess.run([
        sys.executable, "-m", "uvicorn", 
        "app.api:app",
        "--host", "0.0.0.0",
        "--port", "8080", 
        "--reload",
        "--log-level", "info"
    ], check=True)
except KeyboardInterrupt:
    print("\n👋 Backend stopped")
except Exception as e:
    print(f"❌ Error starting backend: {e}")
    sys.exit(1)
