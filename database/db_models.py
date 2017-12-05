
from decimal import *

from sqlalchemy.orm import deferred
from sqlalchemy.orm import relationship

from database import db, db_common

class EmailList(db.Model):
	__tablename__ = 'email_list'

	email = db.Column(db.String(255), primary_key=True, autoincrement=False)
	unsubscribed = db.Column(db.Boolean(), unique=False)

	def __str__(self):
		return '%s' % (self.email)