import datetime
from dateutil.relativedelta import relativedelta

from dateutil import tz

def utcnow():
	return datetime.datetime.now(tz.tzutc()) #+relativedelta(months=3)

def fromtimestamp(utc_timestamp):
	return datetime.datetime.fromtimestamp(float(utc_timestamp), tz=tz.tzutc())

def days_before_now(days_interval):
	return utcnow() - datetime.timedelta(days=days_interval)

def hours_before_now(hours_interval):
	return utcnow() - datetime.timedelta(hours=hours_interval)