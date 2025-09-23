"""add timeclock tables

Revision ID: 20250922_0001
Revises: 20250106_0003
Create Date: 2025-09-22 01:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250922_0001'
down_revision = '20250106_0003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create timeclock_job_site table
    op.create_table('timeclock_job_site',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('latitude', sa.Numeric(precision=10, scale=8), nullable=True),
        sa.Column('longitude', sa.Numeric(precision=11, scale=8), nullable=True),
        sa.Column('radius_meters', sa.Integer(), nullable=True),
        sa.Column('qr_code_data', sa.String(length=500), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_by_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['created_by_id'], ['auth_user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('qr_code_data')
    )
    
    # Create timeclock_time_entry table
    op.create_table('timeclock_time_entry',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('job_site_id', sa.String(), nullable=False),
        sa.Column('clock_in_time', sa.DateTime(), nullable=False),
        sa.Column('clock_out_time', sa.DateTime(), nullable=True),
        sa.Column('break_start_time', sa.DateTime(), nullable=True),
        sa.Column('break_end_time', sa.DateTime(), nullable=True),
        sa.Column('total_hours', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('break_hours', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('clock_in_location_lat', sa.Numeric(precision=10, scale=8), nullable=True),
        sa.Column('clock_in_location_lng', sa.Numeric(precision=11, scale=8), nullable=True),
        sa.Column('clock_out_location_lat', sa.Numeric(precision=10, scale=8), nullable=True),
        sa.Column('clock_out_location_lng', sa.Numeric(precision=11, scale=8), nullable=True),
        sa.Column('is_approved', sa.Boolean(), nullable=True),
        sa.Column('approved_by_id', sa.String(), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['approved_by_id'], ['auth_user.id'], ),
        sa.ForeignKeyConstraint(['job_site_id'], ['timeclock_job_site.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['auth_user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create timeclock_time_entry_audit table
    op.create_table('timeclock_time_entry_audit',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('time_entry_id', sa.String(), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('old_values', sa.Text(), nullable=True),
        sa.Column('new_values', sa.Text(), nullable=True),
        sa.Column('performed_by_id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['performed_by_id'], ['auth_user.id'], ),
        sa.ForeignKeyConstraint(['time_entry_id'], ['timeclock_time_entry.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for better performance
    op.create_index('ix_timeclock_job_site_is_active', 'timeclock_job_site', ['is_active'])
    op.create_index('ix_timeclock_job_site_created_by_id', 'timeclock_job_site', ['created_by_id'])
    op.create_index('ix_timeclock_time_entry_user_id', 'timeclock_time_entry', ['user_id'])
    op.create_index('ix_timeclock_time_entry_job_site_id', 'timeclock_time_entry', ['job_site_id'])
    op.create_index('ix_timeclock_time_entry_clock_in_time', 'timeclock_time_entry', ['clock_in_time'])
    op.create_index('ix_timeclock_time_entry_is_approved', 'timeclock_time_entry', ['is_approved'])
    op.create_index('ix_timeclock_time_entry_audit_time_entry_id', 'timeclock_time_entry_audit', ['time_entry_id'])
    op.create_index('ix_timeclock_time_entry_audit_timestamp', 'timeclock_time_entry_audit', ['timestamp'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_timeclock_time_entry_audit_timestamp')
    op.drop_index('ix_timeclock_time_entry_audit_time_entry_id')
    op.drop_index('ix_timeclock_time_entry_is_approved')
    op.drop_index('ix_timeclock_time_entry_clock_in_time')
    op.drop_index('ix_timeclock_time_entry_job_site_id')
    op.drop_index('ix_timeclock_time_entry_user_id')
    op.drop_index('ix_timeclock_job_site_created_by_id')
    op.drop_index('ix_timeclock_job_site_is_active')
    
    # Drop tables
    op.drop_table('timeclock_time_entry_audit')
    op.drop_table('timeclock_time_entry')
    op.drop_table('timeclock_job_site')
