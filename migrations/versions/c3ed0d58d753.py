"""Add circulating supply

Revision ID: c3ed0d58d753
Revises: 50be9a6a7f7a
Create Date: 2020-06-05 14:58:15.471738

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c3ed0d58d753'
down_revision = '50be9a6a7f7a'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('circulating_supply',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('snapshot_date', sa.DateTime(timezone=True), server_default=sa.text(u'now()'), nullable=True),
    sa.Column('supply_amount', sa.Float(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text(u'now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('circulating_supply')
