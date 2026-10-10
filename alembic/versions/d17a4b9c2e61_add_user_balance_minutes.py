"""add user balance minutes

Revision ID: d17a4b9c2e61
Revises: c264ad6965e2
Create Date: 2026-10-10
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d17a4b9c2e61"
down_revision: Union[str, Sequence[str], None] = "c264ad6965e2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Existing users start with 0 minutes; registration explicitly grants 120.
    op.add_column(
        "user",
        sa.Column(
            "balance_minutes",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("user", "balance_minutes")
