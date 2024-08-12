"""Initialise DBCA Logs Table

Revision ID: e50f91110459
Revises: 94a5398db0ed
Create Date: 2024-05-02 07:53:07.738488

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e50f91110459'
down_revision = '94a5398db0ed'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        u"dbca_logs",
        sa.Column(u"id", sa.UnicodeText),
        sa.Column(u"timestamp", sa.UnicodeText),
        sa.Column(u"level", sa.UnicodeText),
        sa.Column(u"name", sa.UnicodeText),
        sa.Column(u"message", sa.UnicodeText)
    )


def downgrade():
    op.drop_table(u"dbca_logs")
