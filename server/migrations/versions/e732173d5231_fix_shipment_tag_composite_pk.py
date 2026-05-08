"""fix shipment_tag composite pk

Revision ID: e732173d5231
Revises: b5883a213e0c
Create Date: 2026-05-04 22:49:35.115717

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'e732173d5231'
down_revision: Union[str, Sequence[str], None] = 'b5883a213e0c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("shipment_tag") as batch_op:
        batch_op.drop_constraint("shipment_tag_pkey", type_="primary")
        batch_op.create_primary_key(
            "shipment_tag_pkey",
            ["shipment_id", "tag_id"],
        )


def downgrade() -> None:
    """Downgrade schema."""
    # Keep one tag per shipment so we can recreate the old single-column PK.
    op.execute(
        """
        DELETE FROM shipment_tag a
        USING shipment_tag b
        WHERE a.shipment_id = b.shipment_id
          AND a.ctid > b.ctid
        """
    )

    with op.batch_alter_table("shipment_tag") as batch_op:
        batch_op.drop_constraint("shipment_tag_pkey", type_="primary")
        batch_op.create_primary_key("shipment_tag_pkey", ["shipment_id"])
