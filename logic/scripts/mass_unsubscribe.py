# Script for mass unsubscribing emails.
# Sets the 'unsubscribed' flag in the table email_list and
# calls SendGrid to remove the email from all mailing lists.
# Takes as input either a csv file having an email on each line or reads all rows
# that are marked as unsubscribed in the email_list table.

import argparse
import csv
import re
import requests
import sys
import traceback

from time import sleep

from database import db_models
from logic.emails import mailing_list
from tools import db_utils

BATCH_SIZE = 100
SLEEP_SEC = 1.0

def process_batch(emails, update_sg, update_db, do_it):
    if not len(emails):
        return True
    print('{} mode. Unsubscribing {} Update SG={} Update DB={}'.format(
        'Prod' if do_it else 'Dry-run',
        emails, 
        update_sg,
        update_db
    ))
    if not do_it:
        return True
    try:
        if update_sg:
            # Call SendGrid to remove the emails from all mailing lists.
            mailing_list.mass_unsubscribe_sendgrid_contact(emails)
        if update_db:
            # Set the 'unsubscribed' flag on the email_list table.
            for email in emails:
                mailing_list.unsubscribe(email)
    except Exception as e:
        print('ERROR process_batch:', type(e), e)
        traceback.print_exc()
        return False
    return True

def process_filename(filename, do_it):
    print('Starting mass unsubscribe. Loading data from {}'.format(filename))

    # Init stats.
    num = 0
    num_skip = 0
    num_success = 0
    num_failure = 0
    emails = []

    # Iterate thru all the entries from the csv input file.
    with open(filename, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            num += 1
            if num == 1:
                # Skip the header.
                continue
            email = row[0].strip()

            if not email or not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
                print('Empty or invalid email. Skipping row %d.', num)
                num_skip += 1
                continue

            emails.append(email)
            if len(emails) < BATCH_SIZE:
                continue

            # Process the batch.
            success = process_batch(emails, True, True, do_it)
            if success:
                num_success += len(emails)
            else:
                num_failure += len(emails)
            print('%d entries processed' % num)
            emails = []

            # Sleep before processing the next entry for rate limiting purposes.
            sleep(SLEEP_SEC)

       # Process the last batch.
        success = process_batch(emails, True, True, do_it)
        if success:
            num_success += len(emails)
        else:
            num_failure += len(emails)

    print('Processed {} entries. {} skipped {} successes {} failures'.format(
        num,
        num_skip,
        num_success,
        num_failure
    ))


def process_from_db(do_it):
    print('Starting mass unsubscribe. Loading data from DB')

    # Init stats.
    num = 0
    num_skip = 0
    num_success = 0
    num_failure = 0
    emails = []

    # Iterate thru all the entries that are marked as unsubscribed in the DB.
    EmailList = db_models.EmailList
    for row in EmailList.query.filter(EmailList.unsubscribed == True).all():
        num += 1
        email = row.email
        if not email or not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
            print('Empty or invalid email. Skipping row %d.', num)
            num_skip += 1
            continue

        emails.append(email)
        if len(emails) < BATCH_SIZE:
            continue

        # Process the batch.
        success = process_batch(emails, True, False, do_it)
        if success:
            num_success += len(emails)
        else:
            num_failure += len(emails)
        print('{} entries processed'.format(num))
        emails = []

        # Sleep before processing the next entry for rate limiting purposes.
        sleep(SLEEP_SEC)

   # Process the last batch.
    success = process_batch(emails, True, False, do_it)
    if success:
        num_success += len(emails)
    else:
        num_failure += len(emails)

    print('Processed {} entries. {} skipped {} successes {} failures'.format(
        num,
        num_skip,
        num_success,
        num_failure
    ))

def main(filename, from_db, do_it):
    if filename:
        process_filename(filename, do_it)
    elif from_db:
        process_from_db(do_it)
    else:
        raise Error('Invalid filename or from_db arg')

if __name__ == '__main__':
    with db_utils.request_context():
        parser = argparse.ArgumentParser()
        parser.add_argument('--filename', action='store')
        parser.add_argument('--from_db', action='store_true')
        parser.add_argument('--do_it', action='store_true')
        args = parser.parse_args()
        main(args.filename, args.from_db, args.do_it)