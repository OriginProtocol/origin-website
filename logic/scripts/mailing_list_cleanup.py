# called periodically via a cron to cleanup emails that bounce, report us as spam, etc
# so that we mark them as bad and stop emailing them

from logic.emails import mailing_list
from tools import db_utils

if __name__ == '__main__':
    with db_utils.request_context():
        mailing_list.list_cleanup()