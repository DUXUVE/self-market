"""add default categories

Revision ID: c264ad6965e2
Revises: 713db32f59b1
Create Date: 2026-10-08 19:08:29.548820

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c264ad6965e2"
down_revision: Union[str, Sequence[str], None] = "713db32f59b1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Добавляет начальные категории."""

    category_table = sa.table(
        "category",
        sa.column("title", sa.String),
    )

    op.bulk_insert(
        category_table,
        [
            {"title": "Домашние дела"},
            {"title": "IT и техника"},
            {"title": "Курьерские услуги"},
            {"title": "Обучение"},
        ],
    )


def downgrade() -> None:
    """Удаляет начальные категории."""

    op.execute(
        sa.text(
            """
            DELETE FROM category
            WHERE title IN (
                'Домашние дела',
                'IT и техника',
                'Курьерские услуги',
                'Обучение'
            )
            """
        )
    )
    