"""Add user_id to inventory_items for user-specific inventory

Revision ID: 20250922_0003
Revises: 20250906_0002
Create Date: 2025-09-22 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20250922_0003'
down_revision: Union[str, None] = '20250906_0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add user profile fields to auth_user if they don't exist
    op.add_column('auth_user', sa.Column('phone', sa.String(20), nullable=True))
    op.add_column('auth_user', sa.Column('department', sa.String(100), nullable=True))
    op.add_column('auth_user', sa.Column('notes', sa.Text(), nullable=True))
    
    # Add user_id to inventory_items for user-specific inventory
    op.add_column('inventory_items', sa.Column('user_id', sa.String(), nullable=True))
    
    # Create foreign key constraint
    op.create_foreign_key(
        'fk_inventory_items_user_id', 
        'inventory_items', 
        'auth_user', 
        ['user_id'], 
        ['id']
    )
    
    # Create index for performance
    op.create_index('idx_inventory_items_user_id', 'inventory_items', ['user_id'])
    
    # Update existing inventory items to belong to the first admin user
    # This ensures existing data has proper ownership
    op.execute("""
        UPDATE inventory_items 
        SET user_id = (
            SELECT id FROM auth_user 
            WHERE role IN ('admin', 'superadmin') 
            ORDER BY created_at ASC 
            LIMIT 1
        )
        WHERE user_id IS NULL
    """)


def downgrade() -> None:
    # Remove index
    op.drop_index('idx_inventory_items_user_id', 'inventory_items')
    
    # Remove foreign key constraint
    op.drop_constraint('fk_inventory_items_user_id', 'inventory_items', type_='foreignkey')
    
    # Remove user_id column
    op.drop_column('inventory_items', 'user_id')
    
    # Remove user profile fields
    op.drop_column('auth_user', 'notes')
    op.drop_column('auth_user', 'department')
    op.drop_column('auth_user', 'phone')
