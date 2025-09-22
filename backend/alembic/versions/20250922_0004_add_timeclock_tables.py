"""Add timeclock tables (job sites, time entries, audits)

Revision ID: 20250922_0004
Revises: 20250922_0003
Create Date: 2025-09-22 12:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20250922_0004"
down_revision: Union[str, None] = "20250922_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # timeclock_job_site
    op.create_table(
        "timeclock_job_site",
        sa.Column("id", sa.String(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("latitude", sa.Numeric(10, 8), nullable=True),
        sa.Column("longitude", sa.Numeric(11, 8), nullable=True),
        sa.Column("radius_meters", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("qr_code_data", sa.String(length=500), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_by_id", sa.String(), sa.ForeignKey("auth_user.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint("qr_code_data", name="uq_timeclock_job_site_qr_code_data"),
    )
    op.create_index(
        "ix_timeclock_job_site_active",
        "timeclock_job_site",
        ["is_active"],
        unique=False,
    )

    # timeclock_time_entry
    op.create_table(
        "timeclock_time_entry",
        sa.Column("id", sa.String(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.String(), sa.ForeignKey("auth_user.id"), nullable=False),
        sa.Column(
            "job_site_id",
            sa.String(),
            sa.ForeignKey("timeclock_job_site.id"),
            nullable=False,
        ),
        sa.Column("clock_in_time", sa.DateTime(), nullable=False),
        sa.Column("clock_out_time", sa.DateTime(), nullable=True),
        sa.Column("break_start_time", sa.DateTime(), nullable=True),
        sa.Column("break_end_time", sa.DateTime(), nullable=True),
        sa.Column("total_hours", sa.Numeric(5, 2), nullable=True),
        sa.Column("break_hours", sa.Numeric(5, 2), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("clock_in_location_lat", sa.Numeric(10, 8), nullable=True),
        sa.Column("clock_in_location_lng", sa.Numeric(11, 8), nullable=True),
        sa.Column("clock_out_location_lat", sa.Numeric(10, 8), nullable=True),
        sa.Column("clock_out_location_lng", sa.Numeric(11, 8), nullable=True),
        sa.Column("is_approved", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("approved_by_id", sa.String(), sa.ForeignKey("auth_user.id"), nullable=True),
        sa.Column("approved_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(
        "ix_timeclock_time_entry_user_active",
        "timeclock_time_entry",
        ["user_id", "clock_out_time"],
        unique=False,
    )

    # timeclock_time_entry_audit
    op.create_table(
        "timeclock_time_entry_audit",
        sa.Column("id", sa.String(), primary_key=True, nullable=False),
        sa.Column(
            "time_entry_id",
            sa.String(),
            sa.ForeignKey("timeclock_time_entry.id"),
            nullable=False,
        ),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("old_values", sa.Text(), nullable=True),
        sa.Column("new_values", sa.Text(), nullable=True),
        sa.Column("performed_by_id", sa.String(), sa.ForeignKey("auth_user.id"), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
    )
    op.create_index(
        "ix_timeclock_time_entry_audit_time_entry",
        "timeclock_time_entry_audit",
        ["time_entry_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_timeclock_time_entry_audit_time_entry", table_name="timeclock_time_entry_audit")
    op.drop_table("timeclock_time_entry_audit")
    op.drop_index("ix_timeclock_time_entry_user_active", table_name="timeclock_time_entry")
    op.drop_table("timeclock_time_entry")
    op.drop_index("ix_timeclock_job_site_active", table_name="timeclock_job_site")
    op.drop_table("timeclock_job_site")


