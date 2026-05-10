"""add_cancelled_shipmentstatus

Revision ID: e2eb8ba66dd4
Revises: 62bb47fb0c10
Create Date: 2026-05-01 19:40:13.547558

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'e2eb8ba66dd4'
down_revision: Union[str, Sequence[str], None] = '62bb47fb0c10'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add `cancelled` to the ShipmentStatus enum if it's missing."""
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM pg_type t
                JOIN pg_namespace n ON n.oid = t.typnamespace
                WHERE t.typname = 'shipmentstatus'
                  AND n.nspname = 'public'
            ) THEN
                ALTER TYPE public.shipmentstatus ADD VALUE IF NOT EXISTS 'cancelled';
            END IF;
        END
        $$;
        """
    )


def downgrade() -> None:
    """PostgreSQL enum value removal is not safely reversible in-place."""
    pass
