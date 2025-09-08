-- DIRECT DATABASE FIX FOR UE HUB
-- Run this SQL directly on the Neon database to create all required tables

-- 1. Create auth_user table
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

-- Create indexes for auth_user
CREATE INDEX IF NOT EXISTS ix_auth_user_email ON auth_user(email);
CREATE INDEX IF NOT EXISTS ix_auth_user_role ON auth_user(role);
CREATE INDEX IF NOT EXISTS ix_auth_user_is_active ON auth_user(is_active);

-- 2. Create inventory_items table
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

-- Create indexes for inventory_items
CREATE INDEX IF NOT EXISTS ix_inventory_items_sku ON inventory_items(sku);
CREATE INDEX IF NOT EXISTS ix_inventory_items_name ON inventory_items(name);
CREATE INDEX IF NOT EXISTS ix_inventory_items_location ON inventory_items(location);
CREATE INDEX IF NOT EXISTS ix_inventory_items_barcode ON inventory_items(barcode);

-- 3. Create inventory_events table
CREATE TABLE IF NOT EXISTS inventory_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    item_id UUID NOT NULL REFERENCES inventory_items(id),
    actor_id VARCHAR(255),
    delta INTEGER NOT NULL,
    reason VARCHAR(200) NOT NULL,
    meta_json JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create indexes for inventory_events
CREATE INDEX IF NOT EXISTS ix_inventory_events_item_id ON inventory_events(item_id);
CREATE INDEX IF NOT EXISTS ix_inventory_events_actor_id ON inventory_events(actor_id);
CREATE INDEX IF NOT EXISTS ix_inventory_events_created_at ON inventory_events(created_at);

-- 4. Create safety_items table
CREATE TABLE IF NOT EXISTS safety_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category VARCHAR(100) NOT NULL,
    number VARCHAR(20) NOT NULL,
    text TEXT NOT NULL,
    is_critical BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create indexes for safety_items
CREATE INDEX IF NOT EXISTS ix_safety_items_category ON safety_items(category);
CREATE INDEX IF NOT EXISTS ix_safety_items_number ON safety_items(number);
CREATE INDEX IF NOT EXISTS ix_safety_items_is_critical ON safety_items(is_critical);

-- 5. Create safety_checklists table
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

-- Create indexes for safety_checklists
CREATE INDEX IF NOT EXISTS ix_safety_checklists_inspector_id ON safety_checklists(inspector_id);
CREATE INDEX IF NOT EXISTS ix_safety_checklists_status ON safety_checklists(status);
CREATE INDEX IF NOT EXISTS ix_safety_checklists_inspection_date ON safety_checklists(inspection_date);

-- 6. Create safety_checklist_items table
CREATE TABLE IF NOT EXISTS safety_checklist_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    checklist_id UUID NOT NULL REFERENCES safety_checklists(id) ON DELETE CASCADE,
    item_id UUID NOT NULL REFERENCES safety_items(id),
    status VARCHAR(10),
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create indexes for safety_checklist_items
CREATE INDEX IF NOT EXISTS ix_safety_checklist_items_checklist_id ON safety_checklist_items(checklist_id);
CREATE INDEX IF NOT EXISTS ix_safety_checklist_items_item_id ON safety_checklist_items(item_id);
CREATE INDEX IF NOT EXISTS ix_safety_checklist_items_status ON safety_checklist_items(status);

-- 7. Create admin user with bcrypt-hashed password
-- Password: Admin123!@# 
-- This is a bcrypt hash of "Admin123!@#"
INSERT INTO auth_user (id, email, name, role, password_hash, is_active, created_at, updated_at)
VALUES (
    gen_random_uuid()::text, 
    'admin@uehub.com', 
    'Admin User', 
    'superadmin', 
    '$2b$12$LQv3c1yqBwlVHpPjrCXMyeHjNR6HRkqNAi6FgOO6tNMFwGTZ7TFqC',  -- Admin123!@#
    true, 
    NOW(), 
    NOW()
)
ON CONFLICT (email) DO UPDATE SET
    password_hash = EXCLUDED.password_hash,
    role = EXCLUDED.role,
    updated_at = NOW();

-- 8. Insert some sample safety items for OSHA compliance
INSERT INTO safety_items (category, number, text, is_critical) VALUES
('General', '1.1', 'All workers have received proper safety training', true),
('General', '1.2', 'Personal protective equipment (PPE) is available and in good condition', true),
('General', '1.3', 'Safety data sheets (SDS) are available for all hazardous materials', false),
('Scaffolding', '2.1', 'Scaffold is erected on solid, level foundation', true),
('Scaffolding', '2.2', 'All scaffold components are in good condition', true),
('Scaffolding', '2.3', 'Guardrails are installed at all open sides and ends', true),
('Scaffolding', '2.4', 'Access ladders are properly secured', true),
('Fall Protection', '3.1', 'Fall protection systems are in place for work above 6 feet', true),
('Fall Protection', '3.2', 'Safety harnesses are inspected and in good condition', true),
('Fall Protection', '3.3', 'Anchor points are properly rated and installed', true)
ON CONFLICT DO NOTHING;

-- Verify tables were created
SELECT 'auth_user' as table_name, count(*) as record_count FROM auth_user
UNION ALL
SELECT 'inventory_items', count(*) FROM inventory_items
UNION ALL
SELECT 'safety_items', count(*) FROM safety_items
UNION ALL
SELECT 'safety_checklists', count(*) FROM safety_checklists;

-- Show admin user
SELECT id, email, name, role, is_active, created_at FROM auth_user WHERE email = 'admin@uehub.com';
