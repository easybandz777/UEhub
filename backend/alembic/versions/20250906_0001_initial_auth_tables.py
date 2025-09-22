"""Initial auth tables

Revision ID: 20250906_0001
Revises: 
Create Date: 2025-09-06 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20250906_0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create auth_user table
    op.create_table('auth_user',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_auth_user_email'), 'auth_user', ['email'], unique=True)
    
    # Create safety_checklists table
    op.create_table('safety_checklists',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('project_name', sa.String(length=200), nullable=False),
        sa.Column('location', sa.String(length=200), nullable=False),
        sa.Column('inspector_id', sa.String(), nullable=False),
        sa.Column('inspection_date', sa.DateTime(), nullable=False),
        sa.Column('scaffold_type', sa.String(length=100), nullable=False),
        sa.Column('height', sa.String(length=50), nullable=False),
        sa.Column('contractor', sa.String(length=200), nullable=True),
        sa.Column('permit_number', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('total_items', sa.Integer(), nullable=False),
        sa.Column('passed_items', sa.Integer(), nullable=False),
        sa.Column('failed_items', sa.Integer(), nullable=False),
        sa.Column('na_items', sa.Integer(), nullable=False),
        sa.Column('critical_failures', sa.Integer(), nullable=False),
        sa.Column('approved_by_id', sa.String(), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['approved_by_id'], ['auth_user.id'], ),
        sa.ForeignKeyConstraint(['inspector_id'], ['auth_user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create safety_checklist_items table
    op.create_table('safety_checklist_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('checklist_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('item_number', sa.String(length=10), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_critical', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['checklist_id'], ['safety_checklists.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create safety_templates table
    op.create_table('safety_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('version', sa.String(length=20), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('template_data', sa.JSON(), nullable=False),
        sa.Column('created_by_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['created_by_id'], ['auth_user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('safety_templates')
    op.drop_table('safety_checklist_items')
    op.drop_table('safety_checklists')
    op.drop_index(op.f('ix_auth_user_email'), table_name='auth_user')
    op.drop_table('auth_user')
