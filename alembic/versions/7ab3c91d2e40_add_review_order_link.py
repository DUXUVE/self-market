"""add reviewer and order to reviews

Revision ID: 7ab3c91d2e40
Revises: f5a82d91c740
Create Date: 2026-10-10
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7ab3c91d2e40"
down_revision: Union[str, Sequence[str], None] = "f5a82d91c740"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "review",
        sa.Column("reviewer_id", sa.BigInteger(), nullable=True),
    )
    op.add_column(
        "review",
        sa.Column("order_id", sa.BigInteger(), nullable=True),
    )
    op.create_foreign_key(
        "fk_review_reviewer_id_user",
        "review",
        "user",
        ["reviewer_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_review_order_id_order",
        "review",
        "order",
        ["order_id"],
        ["id"],
    )
    op.create_unique_constraint(
        "uq_review_order_id",
        "review",
        ["order_id"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_review_order_id", "review", type_="unique")
    op.drop_constraint("fk_review_order_id_order", "review", type_="foreignkey")
    op.drop_constraint("fk_review_reviewer_id_user", "review", type_="foreignkey")
    op.drop_column("review", "order_id")
    op.drop_column("review", "reviewer_id")
