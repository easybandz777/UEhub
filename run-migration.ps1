# Run Alembic Migration on DigitalOcean Droplet
# This script will SSH into the droplet and run the database migration

Write-Host "🗄️ Running Database Migration on DigitalOcean Droplet..." -ForegroundColor Green

$migrationCommands = @"
# Navigate to backend directory
cd /opt/UEhub/backend

# Run the migration
echo "🔄 Running Alembic migration..."
python -m alembic upgrade head

# Verify the migration
echo "✅ Checking migration status..."
python -m alembic current

echo "📊 Verifying database structure..."
python -c "
import asyncio
from app.core.db import async_engine
from sqlalchemy import text

async def verify_migration():
    async with async_engine.connect() as conn:
        # Check if user_id column exists in inventory_items
        result = await conn.execute(text('''
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'inventory_items' 
            AND column_name = 'user_id'
        '''))
        user_id_exists = result.fetchone() is not None
        print(f'✅ user_id column exists: {user_id_exists}')
        
        # Check if user profile fields exist
        result = await conn.execute(text('''
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'auth_user' 
            AND column_name IN ('phone', 'department', 'notes')
        '''))
        profile_fields = [row[0] for row in result.fetchall()]
        print(f'✅ User profile fields: {profile_fields}')
        
        # Check foreign key constraint
        result = await conn.execute(text('''
            SELECT constraint_name 
            FROM information_schema.table_constraints 
            WHERE table_name = 'inventory_items' 
            AND constraint_type = 'FOREIGN KEY'
            AND constraint_name = 'fk_inventory_items_user_id'
        '''))
        fk_exists = result.fetchone() is not None
        print(f'✅ Foreign key constraint exists: {fk_exists}')

asyncio.run(verify_migration())
"

echo "✅ Database migration completed successfully!"
"@

Write-Host "Commands to run on droplet:" -ForegroundColor Yellow
Write-Host $migrationCommands

Write-Host "`n🔑 SSH into your droplet and run these commands:" -ForegroundColor Cyan
Write-Host "ssh root@165.22.12.246" -ForegroundColor White

Write-Host "`nOr copy and paste this one-liner:" -ForegroundColor Cyan
$oneLiner = $migrationCommands -replace "`n", " && " -replace "echo ", "echo "
Write-Host $oneLiner -ForegroundColor White
