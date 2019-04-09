import requests
import collections
import json
import math
from util import time_
from util import sendgrid_wrapper as sgw
from config import constants
from database import db, db_models, db_common
from tools import db_utils
import sys
from ratelimit import limits, sleep_and_retry, RateLimitException
from backoff import on_exception, expo
import re
import time

# NOTE: remember to use lowercase addresses for everything

# token contract addresses
ogn_contract = '0x8207c1ffc5b6804f6024322ccf34f29c3541ae26'
dai_contract = '0x89d24a6b4ccb1b6faa2625fe562bdd9a23260359'

# start tracking a wallet address
def add_contact(address, **kwargs):

	address = address.strip()

	# must look like an ETH address
	if not re.match("^(0x)?[0-9a-fA-F]{40}$", address):
		return False

	contact = db_common.get_or_create(db.session, db_models.EthContact, address=address.lower())

	allowed_fields = ['name','email','phone','investor','presale_interest','investor_airdrop','dapp_user','employee','exchange','company_wallet','desc']
	for key, value in kwargs.items():
		if key in allowed_fields:
			if value:
				setattr(contact, key, value)
		else:
			raise Exception("Unknown field")

	db.session.add(contact)
	db.session.commit()

def lookup_details(address):
	# automatically start tracking every wallet that receives OGN
	contact = db_common.get_or_create(db.session, db_models.EthContact, address=address.lower())
	db.session.add(contact)
	db.session.commit()
	return contact

# limit calls to 5 requests / second per their limits
# https://etherscan.io/apis
@sleep_and_retry
@limits(calls=5, period=1)
def call_etherscan(url):
	raw_json = requests.get(url)
	return raw_json.json()

# limit calls to 3 requests / second per their limits 
# https://amberdata.io/pricing
@sleep_and_retry
@limits(calls=3, period=1)
def call_amberdata(url):
	headers = {'x-api-key': constants.AMBERDATA_KEY}
	raw_json = requests.get(url, headers=headers)
	return raw_json.json()

# track the holdings of every wallet that we're watching
def fetch_eth_balances():

	# etherscan allows us to query the ETH balance of 20 addresses at a time
	chunk = 20

	contacts = db_models.EthContact.query.all()

	groups = [contacts[i * chunk:(i + 1) * chunk] for i in range((len(contacts) + chunk - 1) // chunk )]  
	for group in groups:
		address_list = ",".join([str(x.address) for x in group])

		url = "https://api.etherscan.io/api?module=account&action=balancemulti&address=%s&tag=latest&apikey=%s" % (address_list, constants.ETHERSCAN_KEY)
		results = call_etherscan(url)
		
		try:
			# loop through every wallet we're tracking and update the ETH balance
			for result in results['result']:
				print "Fetching ETH balance for %s" % (result['account'])
				wallet = db_models.EthContact.query.filter_by(address=result['account'].lower()).first()
				# intentionally using ETH instead of WEI to be more human-friendly, despite being less precise
				if result['balance']:
					wallet.eth_balance = float(result['balance'])/math.pow(10, 18)
				else:
					print 'invalid address: %s' % (result['account'])
				db.session.add(wallet)
				db.session.commit()
		except Exception as e:
			print e
			print results

# amberdata seems to have the fastest API
def fetch_token_balances():

	contacts = db_models.EthContact.query.all()

	for contact in contacts:
		print "Fetching token balances for %s" % (contact.address)

		# retry up to 5 times
		for i in range(5):
			try:
				url = "https://web3api.io/api/v1/addresses/%s/tokens?page=0&size=100" % (contact.address)
				results = call_amberdata(url)
				contact.tokens = results['payload']['records']
				contact.token_count = results['payload']['totalRecords']

				for token in results['payload']['records']:
					if token['address'] == ogn_contract:
						contact.ogn_balance = float(token['amount'])/math.pow(10, 18)
					elif token['address'] == dai_contract:
						contact.dai_balance = float(token['amount'])/math.pow(10, 18)
				break
			except Exception as e:
				print e
				time.sleep(1)
				print 'retrying. attempt: %d' % (i)

		db.session.add(contact)
		db.session.commit()
		
# monitor & alert on all movement of OGN
def fetch_ogn_transactions():

	etherscan_url = 'http://api.etherscan.io/api?module=account&action=tokentx&contractaddress=%s&startblock=0&endblock=999999999&sort=desc&apikey=%s' % (ogn_contract, constants.ETHERSCAN_KEY)
	results = call_etherscan(etherscan_url)

	# loop through every transaction where Origin tokens were moved
	for result in results['result']:
		tx = db_common.get_or_create(db.session, db_models.TokenTransaction, tx_hash=result['hash'])
		tx.from_address = result['from'].lower()
		tx.to_address = result['to'].lower()
		# intentionally using ETH instead of WEI to be more human-friendly, despite being less precise
		tx.amount = float(result['value'])/math.pow(10, 18)
		tx.block_number = result['blockNumber']
		tx.timestamp = time_.fromtimestamp(result['timeStamp'])

		if tx.amount > 0:
			print "%g OGN moved in transaction %s from %s to %s" % (tx.amount, result['hash'], tx.from_address, tx.to_address) 

		# send an email alert every time OGN tokens are moved
		# only alert once & ignore marketplace transactions which show up as 0 OGN
		if (tx.amount > 0 and not tx.notification_sent):
			to_details = lookup_details(tx.to_address)
			from_details = lookup_details(tx.from_address)

			if from_details.name and to_details.name:
				subject = "%s moved %g OGN to %s" % (from_details.name, tx.amount, to_details.name)
			elif from_details.name:
				subject = "%s moved %g OGN" % (from_details.name, tx.amount)
			elif to_details.name:
				subject = "%g OGN moved to %s" % (tx.amount, to_details.name)	
			else:
				subject = "%g OGN moved" % (tx.amount)

			body = """
				{amount} OGN <a href='https://etherscan.io/tx/{tx_hash}'>moved</a>
				from <a href='https://etherscan.io/address/{from_address}'>{from_name}</a>
				to <a href='https://etherscan.io/address/{to_address}'>{to_name}</a>
			""".format(
				amount='{0:g}'.format(float(tx.amount)),
				tx_hash=tx.tx_hash,
				from_name=from_details.name if from_details.name else tx.from_address,
				from_address=tx.from_address,
				to_name=to_details.name if to_details.name else tx.to_address,
				to_address=tx.to_address
			)

			# print subject

			sgw.notify_founders(body, subject)
			tx.notification_sent = True
			db.session.add(tx)
			db.session.commit()

# called via cron on Heroku
with db_utils.request_context():
	if len(sys.argv) > 1:
		if sys.argv[1] == 'ogn':
			fetch_ogn_transactions()
		elif sys.argv[1] == 'eth':
			fetch_eth_balances()
		elif sys.argv[1] == 'tokens':
			fetch_token_balances()

	else:
		print 'pass `eth`, `ogn` or `tokens` as an argument when running this script'



