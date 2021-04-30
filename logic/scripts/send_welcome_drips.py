from tools import db_utils
from util import sendgrid_wrapper as sgw
from logic.emails import email_types

# this is called daily using a Heroku cron job

if __name__ == '__main__':
	with db_utils.request_context():

		try:
			email_types.send_welcome_drips()
		except Exception as e:
			print(e)
			sgw.notify_admins("Error sending welcome drips %s" % (e), "Error sending welcome drips")