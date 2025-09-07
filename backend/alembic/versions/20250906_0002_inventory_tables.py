"""Add inventory tables

Revision ID: 20250906_0002
Revises: 20250906_0001
Create Date: 2025-01-09 20:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20250906_0002'
down_revision: Union[str, None] = '20250906_0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create inventory_items table
    op.create_table('inventory_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sku', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('location', sa.String(length=100), nullable=False),
        sa.Column('barcode', sa.String(length=50), nullable=True),
        sa.Column('qty', sa.Integer(), nullable=False),
        sa.Column('min_qty', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_inventory_items_barcode'), 'inventory_items', ['barcode'], unique=False)
    op.create_index(op.f('ix_inventory_items_location'), 'inventory_items', ['location'], unique=False)
    op.create_index(op.f('ix_inventory_items_name'), 'inventory_items', ['name'], unique=False)
    op.create_index(op.f('ix_inventory_items_sku'), 'inventory_items', ['sku'], unique=False)
    op.create_unique_constraint(None, 'inventory_items', ['sku'])

    # Create inventory_events table (without foreign key constraints for now)
    op.create_table('inventory_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('item_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('actor_id', sa.String(), nullable=True),  # Make nullable for now
        sa.Column('delta', sa.Integer(), nullable=False),
        sa.Column('reason', sa.String(length=200), nullable=False),
        sa.Column('meta_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['item_id'], ['inventory_items.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_inventory_events_actor_id'), 'inventory_events', ['actor_id'], unique=False)
    op.create_index(op.f('ix_inventory_events_created_at'), 'inventory_events', ['created_at'], unique=False)
    op.create_index(op.f('ix_inventory_events_item_id'), 'inventory_events', ['item_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_inventory_events_item_id'), table_name='inventory_events')
    op.drop_index(op.f('ix_inventory_events_created_at'), table_name='inventory_events')
    op.drop_index(op.f('ix_inventory_events_actor_id'), table_name='inventory_events')
    op.drop_table('inventory_events')
    op.drop_constraint(None, 'inventory_items', type_='unique')
    op.drop_index(op.f('ix_inventory_items_sku'), table_name='inventory_items')
    op.drop_index(op.f('ix_inventory_items_name'), table_name='inventory_items')
    op.drop_index(op.f('ix_inventory_items_location'), table_name='inventory_items')
    op.drop_index(op.f('ix_inventory_items_barcode'), table_name='inventory_items')
    op.drop_table('inventory_items')
