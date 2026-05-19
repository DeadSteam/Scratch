"""Add mime_type to experiment_images and convert scratch_results to JSONB.

Revision ID: 2026_05_18_mime_jsonb
Revises:
Create Date: 2026-05-18

Audit items B7 + B11. The migration is idempotent so it's safe to run
on databases that were bootstrapped via ``Base.metadata.create_all`` and
already contain the new schema (model-first deployments).
"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from alembic import op

# revision identifiers, used by Alembic.
revision = "2026_05_18_mime_jsonb"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # B11 — mime_type column (nullable: legacy rows fall back to sniffing).
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'experiment_images'
                  AND column_name = 'mime_type'
            ) THEN
                ALTER TABLE experiment_images
                    ADD COLUMN mime_type VARCHAR(50);
            END IF;
        END$$;
        """
    )

    # B7 — scratch_results JSON -> JSONB. No-op if already JSONB.
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'experiments'
                  AND column_name = 'scratch_results'
                  AND data_type = 'json'
            ) THEN
                ALTER TABLE experiments
                    ALTER COLUMN scratch_results TYPE JSONB
                    USING scratch_results::jsonb;
            END IF;
        END$$;
        """
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE experiments "
        "ALTER COLUMN scratch_results TYPE JSON USING scratch_results::json"
    )
    with op.batch_alter_table("experiment_images") as batch:
        batch.drop_column("mime_type")


# Keep imports used so ruff/ty don't flag them.
_ = (JSONB, sa)
