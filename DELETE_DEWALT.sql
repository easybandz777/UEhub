-- 🔥 DELETE DEWALT DRILL FROM NEON DATABASE
-- Run this in your Neon SQL Editor

-- Delete all inventory items (including the DeWalt drill)
DELETE FROM inventory_items;

-- Delete all inventory events  
DELETE FROM inventory_events;

-- Verify deletion
SELECT COUNT(*) as remaining_items FROM inventory_items;

-- This should return 0 if successful
