# Script that takes as input a csv dump of the dapp identity data and calls the website's
# mailing-list/join endpoint to populate the data in the website DB.
# The format of the input csv should be:
# eth_address,email,first_name,last_name,phone,country,ip_addr

import argparse
import csv
import requests
import sys

from time import sleep

PROD_URL = 'https://www.originprotocol.com/mailing-list/join'
STAGING_URL='https://staging.originprotocol.com/mailing-list/join'
LOCAL_URL = 'http://localhost:5000/mailing-list/join'

# Rate limite the number of requests made to the mailing-list/jin endpoint to ~1 per sec.
# This is necessary since internally that endpoint makes calls to the
# SendGrid /contactdb/recipients API which itself is rate limited.
SLEEP_SEC = 1.0 # 1 sec

def process(url, eth_address, email, first_name, last_name, phone, country_code, ip):
    print('Adding entry {} {}'.format(email, eth_address))
    data = {
        'eth_address': eth_address,
        'email': email,
        'first_name': first_name,
        'last_name': last_name,
        'phone': phone,
        'country_code': country_code,
        'ip_addr': ip,
        'dapp_user': 1,
        'backfill': 1
    }
    response = requests.post(url=url, data=data)
    data = response.json()
    print('Response={}'.format(data))
    return data.get('success', False)

def main(filename, url, do_it):
    print('Starting backfill. Loading data from {}'.format(filename))

    # Init stats.
    num = 0
    num_skip = 0
    num_success = 0
    num_failure = 0

    # Iterate thru all the entries from the csv input file.
    with open(filename, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            num += 1
            if num == 1:
                # Skip the header.
                continue
            eth_address = row[0].strip()
            email = row[1].strip()
            first_name = row[2].strip()
            last_name = row[3].strip()
            phone = row[4].strip()
            country_code = row[5].strip()
            ip = row[6].strip()

            if not email:
                print('Empty email. Skipping row %d.', num)
                num_skip += 1
                continue

            # Process the entry.
            if do_it:
                success = process(url, eth_address, email, first_name, last_name, phone, country_code, ip)
            else:
                print('Dry-run: ', eth_address, email, first_name, last_name, phone, country_code, ip)
                success = True

            if success == True:
                num_success += 1
            else:
                num_failure += 1
            print('%d entries processed' % num)

            # Sleep before processing the next entry for rate limiting purposes.
            sleep(SLEEP_SEC)

    print('Processed {} entries. {} skipped {} successes {} failures'.format(num, num_skip, num_success, num_failure))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('--do_it', action='store_true')
    parser.add_argument('--prod', action='store_true')
    parser.add_argument('--staging', action='store_true')
    args = parser.parse_args()
    if args.prod:
        url = PROD_URL
    elif args.staging:
        url = STAGING_URL
    else:
        url = LOCAL_URL
    print('Using URL:', url)
    main(args.filename, url, args.do_it)
