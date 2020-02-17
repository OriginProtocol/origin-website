"""empty message

Revision ID: 24e593efdb89
Revises: 618ce1079e81
Create Date: 2020-02-07 18:38:55.042479

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '24e593efdb89'
down_revision = '618ce1079e81'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('email_list', sa.Column('blocked', sa.Boolean(), nullable=True))
    op.add_column('email_list', sa.Column('bounced', sa.Boolean(), nullable=True))
    op.add_column('email_list', sa.Column('invalid', sa.Boolean(), nullable=True))
    op.add_column('email_list', sa.Column('reported_spam', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('email_list', 'reported_spam')
    op.drop_column('email_list', 'invalid')
    op.drop_column('email_list', 'bounced')
    op.drop_column('email_list', 'blocked')
    # ### end Alembic commands ###