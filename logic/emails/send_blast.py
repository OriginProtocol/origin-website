from logic.emails import mailing_list
from tools import db_utils

with db_utils.request_context():
    mailing_list.send_one_off("coinlist_announcement")
    