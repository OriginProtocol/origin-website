import argparse
import csv
import requests
import sys

URL = 'https://originprotocol.com/mailing-list/join'

def process(eth_address, email, first_name, last_name, phone, country_code)
    print('Adding entry %s %s' % (email, eth_address))
    params = {
        'eth_address': eth_address,
        'email': email,
        'first_name': first_name,
        'last_name': last_name,
        'phone': phone,
        'country_code': country_code,
        'dapp_user': 1
    }
    response = requests.post(url=URL, params=params)
    data = response.json()
    print('Response=%s' %s)
    return data.success

def main(filename, do_it)
    print('Starting backfill. Loading data from %s' % filename)

    # Init stats.
    num = 0
    num_success = 0
    num_failure = 0

    # Iterate thru all the entries from the csv input file.
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            eth_address = row[0]
            email = row[1]
            first_name = row[2]
            last_name = row[3]
            phone = row[4]
            country_code = row[5]

            # Process the entry.
            success = process(eth_address, email, first_name, last_name, phone, country_code)

            if success:
                num_success += 1
            else:
                num_failure += 1
    print('Processed %d entries. %d successes %d failures' % (num, num_success, num_failure)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('do_it')
    args = parser.parse_args()
	main(args.filename, args.do_it)