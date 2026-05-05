"""Add UI fields for knowledge situations.

Revision ID: 20260409_add_situation_ui_fields
Revises:
Create Date: 2026-04-09
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260409_add_situation_ui_fields"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE situation
        ADD COLUMN IF NOT EXISTS label VARCHAR(50),
        ADD COLUMN IF NOT EXISTS severity VARCHAR(20);
        """
    )
    op.execute(
        """
        ALTER TABLE situation
        ALTER COLUMN description TYPE VARCHAR(255);
        """
    )
    op.execute(
        """
        ALTER TABLE cause
        ALTER COLUMN description TYPE VARCHAR(255);
        """
    )
    op.execute(
        """
        ALTER TABLE advice
        ALTER COLUMN description TYPE VARCHAR(255);
        """
    )
    op.execute(
        """
        UPDATE situation
        SET controlled_param = 'delta_scratch_index'
        WHERE controlled_param IS NULL
           OR controlled_param = ''
           OR controlled_param = 'Модуль изменения индекс зарапанности';
        """
    )
    op.execute(
        """
        UPDATE situation
        SET
            label = CASE
                WHEN label IS NOT NULL AND label <> '' THEN label
                WHEN description ILIKE '%хорош%' THEN 'Хорошо'
                WHEN description ILIKE '%средн%' THEN 'Средне'
                WHEN description ILIKE '%плох%' THEN 'Критично'
                ELSE 'Без оценки'
            END,
            severity = CASE
                WHEN severity IS NOT NULL AND severity <> '' THEN severity
                WHEN description ILIKE '%хорош%' THEN 'success'
                WHEN description ILIKE '%средн%' THEN 'warning'
                WHEN description ILIKE '%плох%' THEN 'error'
                ELSE 'muted'
            END;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE situation
        DROP COLUMN IF EXISTS severity,
        DROP COLUMN IF EXISTS label;
        """
    )
    op.execute(
        """
        ALTER TABLE situation
        ALTER COLUMN description TYPE VARCHAR(100);
        """
    )
    op.execute(
        """
        ALTER TABLE cause
        ALTER COLUMN description TYPE VARCHAR(100);
        """
    )
    op.execute(
        """
        ALTER TABLE advice
        ALTER COLUMN description TYPE VARCHAR(50);
        """
    )
