"""Initialise DBCA Spatial Table

Revision ID: 94a5398db0ed
Revises:
Create Date: 2024-02-15 06:26:27.941377

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '94a5398db0ed'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        u"dbca_spatial",
        sa.Column(u"id", sa.UnicodeText, primary_key=True),
        sa.Column(u"label", sa.UnicodeText, nullable=False, unique=True),
        sa.Column(u"geometry", postgresql.JSONB, nullable=False)
    )


def downgrade():
    op.drop_table(u"dbca_spatial")
