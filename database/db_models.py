
from decimal import *

from sqlalchemy.orm import deferred
from sqlalchemy.orm import relationship

from database import db, db_common

class EmailList(db.Model):
	__tablename__ = 'email_list'

	email = db.Column(db.String(255), primary_key=True, autoincrement=False)
	unsubscribed = db.Column(db.Boolean())

	def __str__(self):
		return '%s' % (self.email)

class Presale(db.Model):
	__tablename__ = 'presale'

	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(255))
	accredited = db.Column(db.Boolean())
	entity_type = db.Column(db.String(255))
	desired_allocation = db.Column(db.String(255))
	desired_allocation_currency = db.Column(db.String(3))
	citizenship = db.Column(db.String(2))
	sending_addr = db.Column(db.String(255))
	note = db.Column(db.Text())

	def __str__(self):
		return '%s' % (self.email)