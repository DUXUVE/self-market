"""add wallet operation status and timestamp

Revision ID: f5a82d91c740
Revises: e4b71c9a2f30
Create Date: 2026-10-10
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f5a82d91c740"
down_revision: Union[str, Sequence[str], None] = "e4b71c9a2f30"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "operation",
        sa.Column("status", sa.String(length=30), server_default="completed", nullable=False),
    )
    op.add_column(
        "operation",
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_column("operation", "created_at")
    op.drop_column("operation", "status")
