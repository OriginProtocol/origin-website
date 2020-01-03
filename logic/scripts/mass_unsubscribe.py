# Script for mass unsubscribing emails.
# Sets the 'unsubscribed' flag in the table email_list and
# calls SendGrid to remove the email from all mailing lists.
# Takes as input a csv file having an email on each line.

import argparse
import csv
import re
import requests
import sys
import traceback

from time import sleep

from logic.emails import mailing_list
from tools import db_utils

BATCH_SIZE = 100
SLEEP_SEC = 1.0

def process_batch(emails, do_it):
    if not len(emails):
        return True
    print('%s mode. Unsubscribing %s' % ('Prod' if do_it else 'Dry-run', emails))
    if not do_it:
        return True
    try:
        # Set the 'unsubscribed' flag on the email_list table.
        for email in emails:
            mailing_list.unsubscribe(email)
        # Call SendGrid to remove the emails from all mailing lists.
        #mailing_list.mass_unsubscribe_sendgrid_contact(emails)
    except Exception as e:
        print('ERROR process_batch:', type(e), e)
        traceback.print_exc()
        return False
    return True

def main(filename, do_it):
    print('Starting mass unsubscribe. Loading data from %s' % filename)

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
            success = process_batch(emails, do_it)

            if success:
                num_success += len(emails)
            else:
                num_failure += len(emails)
            print('%d entries processed' % num)
            emails = []

            # Sleep before processing the next entry for rate limiting purposes.
            sleep(SLEEP_SEC)

       # Process the last batch.
        success = process_batch(emails, do_it)
        if success:
            num_success += len(emails)
        else:
            num_failure += len(emails)


    print('Processed %d entries. %s skipped %d successes %d failures' % (num, num_skip, num_success, num_failure))

if __name__ == '__main__':
    with db_utils.request_context():
        parser = argparse.ArgumentParser()
        parser.add_argument('filename')
        parser.add_argument('--do_it', action='store_true')
        args = parser.parse_args()
        main(args.filename, args.do_it)