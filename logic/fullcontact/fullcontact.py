import re

from flask import jsonify, flash, redirect
from database import db, db_common, db_models

def fullcontact(email, response):
    if not re.match(
        r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",
            email):
        return gettext('Please enter a valid email address')

    try:
        me = db_models.FullContact()
        me.email = email
        me.fullcontact_response = response

        if 'socialProfiles' in response:
            profiles = response['socialProfiles']

            for profile in profiles:
                if 'typeId' in profile and 'username' in profile:
                    network = profile['typeId']
                    username = profile['username']

                    if network == 'angellist':
                        me.angellist_handle = username
                    if network == 'github':
                        me.githhub_handle = username
                    if network == 'twitter':
                        me.twitter_handle = username

        db.session.add(me)
        db.session.commit()
    except Exception as e:
        print (e)
        return

    return
