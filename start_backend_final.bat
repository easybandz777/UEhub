@echo off
echo 🚀 Starting UE Hub Backend...
cd backend
set SECRET_KEY=development-secret-key-minimum-32-characters-long-for-local-dev
set DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_EoVzn0WyqX1v@ep-odd-tree-adxsa81s-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require
set CORS_ORIGINS=http://localhost:3000,http://localhost:3001
set ENABLE_DOCS=true
echo ✅ Environment variables set
echo 🔗 Starting server on http://localhost:8000
py -m uvicorn app.api:app --host 0.0.0.0 --port 8000 --reload
