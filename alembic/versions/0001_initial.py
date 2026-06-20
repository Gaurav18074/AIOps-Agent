"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-01-01 00:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "sites",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("url", sa.String(500), nullable=False),
        sa.Column("check_interval_seconds", sa.Integer, server_default="60"),
        sa.Column("enabled", sa.Boolean, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "checks",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("site_id", sa.Integer, sa.ForeignKey("sites.id", ondelete="CASCADE"), index=True),
        sa.Column("status_code", sa.Integer, nullable=True),
        sa.Column("response_time_ms", sa.Float, nullable=True),
        sa.Column("success", sa.Boolean, server_default=sa.false()),
        sa.Column("error", sa.Text, nullable=True),
        sa.Column("checked_at", sa.DateTime, server_default=sa.func.now(), index=True),
    )

    op.create_table(
        "incidents",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("site_id", sa.Integer, sa.ForeignKey("sites.id", ondelete="CASCADE"), index=True),
        sa.Column("severity", sa.String(20), server_default="warning"),
        sa.Column("title", sa.String(500)),
        sa.Column("summary", sa.Text),
        sa.Column("root_cause", sa.Text, nullable=True),
        sa.Column("suggested_fix", sa.Text, nullable=True),
        sa.Column("confidence", sa.Float, nullable=True),
        sa.Column("raw_context", sa.JSON, nullable=True),
        sa.Column("status", sa.String(20), server_default="open"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), index=True),
        sa.Column("resolved_at", sa.DateTime, nullable=True),
    )


def downgrade():
    op.drop_table("incidents")
    op.drop_table("checks")
    op.drop_table("sites")
