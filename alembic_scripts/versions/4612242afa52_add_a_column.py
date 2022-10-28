"""Add a column

Revision ID: 4612242afa52
Revises: 6ddf91e5ea56
Create Date: 2022-10-27 17:42:37.332544

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4612242afa52"
down_revision = "6ddf91e5ea56"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("account", sa.Column("last_transaction_date", sa.DateTime))


def downgrade():
    op.drop_column("account", "last_transaction_date")
