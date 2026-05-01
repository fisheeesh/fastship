"""baseline_existing_schema

Revision ID: 62bb47fb0c10
Revises: 
Create Date: 2026-05-01 19:40:10.662846

"""
from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = '62bb47fb0c10'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Baseline existing schema already present in the database."""
    pass


def downgrade() -> None:
    """No-op downgrade for baseline revision."""
    pass
