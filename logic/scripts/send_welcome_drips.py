from tools import db_utils
from util import sendgrid_wrapper as sgw
from logic.emails import email_types

if __name__ == '__main__':
	with db_utils.request_context():

		try:
			email_types.send_welcome_drips()
		except Exception as e:
			print e
			# sgw.notify_admins("Error sending welcome drips<br><br> %s" % (e), "Error sending welcome drips")