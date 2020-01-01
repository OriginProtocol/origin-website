import csv
import requests

from database import db_models

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

def main(filename)
    print('Starting backfill...')

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
	# called via cron on Heroku
	with db_utils.request_context():
		main()