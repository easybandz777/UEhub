# EMERGENCY DATABASE INITIALIZATION

## Problem
The UE Hub application is experiencing 500 Internal Server Errors because the database tables don't exist in the Neon PostgreSQL database.

## Solution
Run the SQL commands below directly in the Neon database console to create all required tables and the admin user.

## Steps to Fix

### 1. Access Neon Database Console
1. Go to https://console.neon.tech/
2. Select your project: `ep-odd-tree-adxsa81s`
3. Go to the SQL Editor
4. Connect to the `neondb` database

### 2. Execute This SQL (Copy and paste all at once):

```sql
-- Create auth_user table
CREATE TABLE IF NOT EXISTS auth_user (
    id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid()::text,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'worker',
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_auth_user_email ON auth_user(email);
CREATE INDEX IF NOT EXISTS ix_auth_user_role ON auth_user(role);
CREATE INDEX IF NOT EXISTS ix_auth_user_is_active ON auth_user(is_active);

-- Create inventory_items table
CREATE TABLE IF NOT EXISTS inventory_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    location VARCHAR(100) NOT NULL,
    barcode VARCHAR(50),
    qty INTEGER NOT NULL DEFAULT 0,
    min_qty INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_inventory_items_sku ON inventory_items(sku);
CREATE INDEX IF NOT EXISTS ix_inventory_items_name ON inventory_items(name);
CREATE INDEX IF NOT EXISTS ix_inventory_items_location ON inventory_items(location);

-- Create inventory_events table
CREATE TABLE IF NOT EXISTS inventory_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    item_id UUID NOT NULL REFERENCES inventory_items(id),
    actor_id VARCHAR(255),
    delta INTEGER NOT NULL,
    reason VARCHAR(200) NOT NULL,
    meta_json JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create safety tables
CREATE TABLE IF NOT EXISTS safety_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category VARCHAR(100) NOT NULL,
    number VARCHAR(20) NOT NULL,
    text TEXT NOT NULL,
    is_critical BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS safety_checklists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_name VARCHAR(200) NOT NULL,
    location VARCHAR(200) NOT NULL,
    inspector_id VARCHAR(255) NOT NULL,
    inspection_date DATE NOT NULL,
    scaffold_type VARCHAR(100) NOT NULL,
    height VARCHAR(50) NOT NULL,
    contractor VARCHAR(200),
    permit_number VARCHAR(100),
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    total_items INTEGER NOT NULL DEFAULT 0,
    passed_items INTEGER NOT NULL DEFAULT 0,
    failed_items INTEGER NOT NULL DEFAULT 0,
    na_items INTEGER NOT NULL DEFAULT 0,
    critical_failures INTEGER NOT NULL DEFAULT 0,
    approved_by_id VARCHAR(255),
    approved_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS safety_checklist_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    checklist_id UUID NOT NULL REFERENCES safety_checklists(id) ON DELETE CASCADE,
    item_id UUID NOT NULL REFERENCES safety_items(id),
    status VARCHAR(10),
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create admin user (password: Admin123!@#)
INSERT INTO auth_user (id, email, name, role, password_hash, is_active, created_at, updated_at)
VALUES (
    gen_random_uuid()::text, 
    'admin@uehub.com', 
    'Admin User', 
    'superadmin', 
    '$2b$12$LQv3c1yqBwlVHpPjrCXMyeHjNR6HRkqNAi6FgOO6tNMFwGTZ7TFqC',
    true, 
    NOW(), 
    NOW()
)
ON CONFLICT (email) DO UPDATE SET
    password_hash = EXCLUDED.password_hash,
    role = EXCLUDED.role,
    updated_at = NOW();

-- Insert sample safety items
INSERT INTO safety_items (category, number, text, is_critical) VALUES
('General', '1.1', 'All workers have received proper safety training', true),
('General', '1.2', 'Personal protective equipment (PPE) is available and in good condition', true),
('Scaffolding', '2.1', 'Scaffold is erected on solid, level foundation', true),
('Scaffolding', '2.2', 'All scaffold components are in good condition', true),
('Scaffolding', '2.3', 'Guardrails are installed at all open sides and ends', true),
('Fall Protection', '3.1', 'Fall protection systems are in place for work above 6 feet', true),
('Fall Protection', '3.2', 'Safety harnesses are inspected and in good condition', true)
ON CONFLICT DO NOTHING;
```

### 3. Verify Tables Were Created

Run this to check:

```sql
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
SELECT email, name, role FROM auth_user WHERE email = 'admin@uehub.com';
```

### 4. Test the Application

After running the SQL:

1. Go to your website
2. Try to login with:
   - **Email:** admin@uehub.com
   - **Password:** Admin123!@#

## Expected Result

✅ Login should work  
✅ Dashboard should load  
✅ Inventory and Safety features should be accessible  

## If It Still Doesn't Work

1. Check the Neon database logs
2. Verify the database URL in your Fly.io environment variables
3. Make sure the Fly.io app has redeployed with the latest code

## Login Credentials

**Email:** admin@uehub.com  
**Password:** Admin123!@#  
**Role:** superadmin  

## Files Created

- `DIRECT_DATABASE_FIX.sql` - Complete SQL script
- `backend/app/modules/auth/models.py` - Fixed auth models
- Updated repository to use correct table names
- Fixed CORS configuration

The database tables MUST be created manually in Neon console for the application to work.
