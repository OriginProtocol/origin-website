"""import data to EmailList

Revision ID: 7f2cc42f04f6
Revises: 2627b59a3f8b
Create Date: 2018-03-22 16:02:46.642468

"""
from alembic import op
from sqlalchemy.orm.session import sessionmaker

from database.db_models import Presale, Interest, EmailList

# revision identifiers, used by Alembic.
revision = '7f2cc42f04f6'
down_revision = '2627b59a3f8b'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    session_instance = sessionmaker(bind=connection.engine)
    session = session_instance(bind=connection)
    for obj in session.query(Presale).filter(~Presale.email.in_(session.query(EmailList.email))):
        session.add(EmailList(email=obj.email, unsubscribed=False))
    for obj in session.query(Interest).filter(~Interest.email.in_(session.query(EmailList.email))):
        session.add(EmailList(email=obj.email, unsubscribed=False))
    session.flush()


def downgrade():
    pass
