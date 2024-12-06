"""Initial migration

Revision ID: ce669a1451b3
Revises: 
Create Date: 2024-12-06 15:56:08.241734

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ce669a1451b3"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "parcel_types",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(
        op.f("ix_parcel_types_id"), "parcel_types", ["id"], unique=False
    )
    op.create_table(
        "parcels",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.Column("content_value", sa.Float(), nullable=False),
        sa.Column("delivery_cost", sa.Float(), nullable=True),
        sa.Column("type_id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["type_id"],
            ["parcel_types.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_parcels_id"), "parcels", ["id"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_parcels_id"), table_name="parcels")
    op.drop_table("parcels")
    op.drop_index(op.f("ix_parcel_types_id"), table_name="parcel_types")
    op.drop_table("parcel_types")
    # ### end Alembic commands ###