"""init jobs/agent_runs/artifacts
Revision ID: jobs_agent_runs_artifacts_0001
Revises: 9d5a86746acc  # ajusta al último hash tuyo si difiere
Create Date: 2025-09-28 00:01:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "jobs_agent_runs_artifacts_0001"
down_revision = "9d5a86746acc"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("agent", sa.String(length=50), nullable=False),
        sa.Column("state", sa.String(length=20), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("run_after", sa.DateTime(timezone=True)),
        sa.Column("last_error", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "agent_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("agent", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("logs", sa.Text()),
        sa.Column("details_json", sa.Text()),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.Column("ended_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "artifacts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("kind", sa.String(length=30), nullable=False),
        sa.Column("path", sa.String(length=512), nullable=False),
        sa.Column("size", sa.Integer()),
        sa.Column("sha256", sa.String(length=64)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )

def downgrade():
    op.drop_table("artifacts")
    op.drop_table("agent_runs")
    op.drop_table("jobs")
