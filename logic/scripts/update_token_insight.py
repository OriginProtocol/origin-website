import collections
from datetime import datetime, timedelta
import json
import math
import re
import sys
import time
import os

from backoff import on_exception, expo
from config import constants, universal
from database import db, db_models, db_common
from ratelimit import limits, sleep_and_retry, RateLimitException
import requests
from tools import db_utils
from util import sendgrid_wrapper as sgw
from util import time_

import json

from logic.scripts import token_stats

# NOTE: remember to use lowercase addresses for everything

# start tracking a wallet address
def add_contact(address, **kwargs):

    # nothing to do here, bail
    if not address:
        return False

    address = address.strip()

    # must look like an ETH address
    if not re.match("^(0x)?[0-9a-fA-F]{40}$", address):
        return False

    contact = db_common.get_or_create(
        db.session, db_models.EthContact, address=address.lower()
    )

    allowed_fields = [
        "name",
        "email",
        "phone",
        "investor",
        "presale_interest",
        "investor_airdrop",
        "dapp_user",
        "employee",
        "exchange",
        "company_wallet",
        "desc",
        "country_code",
    ]
    for key, value in kwargs.items():
        if key in allowed_fields:
            if value:
                # Normalize email to lower case before storing in the DB.
                if key == "email":
                    value = value.lower()
                setattr(contact, key, value)
        else:
            raise Exception("Unknown field")

    db.session.add(contact)
    db.session.commit()


def lookup_details(address):
    # automatically start tracking every wallet that receives OGN
    contact = db_common.get_or_create(
        db.session, db_models.EthContact, address=address.lower()
    )
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
    headers = {"x-api-key": constants.AMBERDATA_KEY}
    raw_json = requests.get(url, headers=headers)
    return raw_json.json()


# limit calls to 10 requests / second per their limits
# https://github.com/EverexIO/Ethplorer/wiki/Ethplorer-API#api-keys-limits
@sleep_and_retry
@limits(calls=10, period=1)
def call_ethplorer(url):
    url = "%s?apiKey=%s" % (url, constants.ETHPLORER_KEY)
    raw_json = requests.get(url)
    return raw_json.json()


# this script is called on a 10 minute cron by Heroku
# break things up so we update slowly throughout the day instead of in one big batch
def get_some_contacts():
    per_run = 24 * 6  # every ten minutes
    total = db.session.query(db_models.EthContact.address).count()
    limit = int(total / per_run) + 1
    print("checking {} wallets".format(limit))
    EC = db_models.EthContact
    return (
        EC.query.filter(EC.last_updated < time_.days_before_now(1))
        .order_by(EC.last_updated)
        .limit(limit)
        .all()
    )


# track the holdings of every wallet that we're watching
def fetch_eth_balances_from_etherscan():

    # etherscan allows us to query the ETH balance of 20 addresses at a time
    chunk = 20

    contacts = get_some_contacts()

    groups = [
        contacts[i * chunk : (i + 1) * chunk]
        for i in range((len(contacts) + chunk - 1) // chunk)
    ]
    for group in groups:
        address_list = ",".join([str(x.address) for x in group])

        url = (
            "https://api.etherscan.io/api?module=account&action=balancemulti&address=%s&tag=latest&apikey=%s"
            % (address_list, constants.ETHERSCAN_KEY)
        )
        results = call_etherscan(url)

        try:
            # loop through every wallet we're tracking and update the ETH balance
            for result in results["result"]:
                print("Fetching ETH balance for {}".format(result["account"]))
                wallet = db_models.EthContact.query.filter_by(
                    address=result["account"].lower()
                ).first()
                # intentionally using ETH instead of WEI to be more human-friendly, despite being less precise
                if result["balance"]:
                    wallet.eth_balance = float(result["balance"]) / math.pow(10, 18)
                else:
                    print("invalid address: {}".format(result["account"]))
                wallet.last_updated = datetime.utcnow()
                db.session.add(wallet)
                db.session.commit()
        except Exception as e:
            print(e)
            print(results)


# amberdata seems to have the fastest API
def fetch_tokens_from_amberdata():

    contacts = get_some_contacts()

    for contact in contacts:
        print("Fetching token balances for {}".format(contact.address))

        contact.tokens = []

        per_page = 100
        page = 0

        keep_looking = True

        # pagination
        while keep_looking:
            try:

                url = (
                    "https://web3api.io/api/v1/addresses/%s/tokens?page=%d&size=%d"
                    % (contact.address, page, per_page)
                )
                print(url)
                results = call_amberdata(url)

                # print(results)

                contact.tokens = contact.tokens + results["payload"]["records"]
                contact.token_count = results["payload"]["totalRecords"]

                print("%s tokens found. fetching page {}".format(contact.token_count, page))

                for token in results["payload"]["records"]:
                    if token["address"] == token_stats.ogn_contract:
                        contact.ogn_balance = float(token["amount"]) / math.pow(10, 18)
                    elif token["address"] == token_stats.dai_contract:
                        contact.dai_balance = float(token["amount"]) / math.pow(10, 18)

                if (
                    int(results["payload"]["totalRecords"]) <= per_page
                    or len(results["payload"]["records"]) < per_page
                ):
                    keep_looking = False
                    break
                else:
                    page = page + 1
            except Exception as e:
                print(e)
                time.sleep(1)
                print("retrying")

        contact.last_updated = datetime.utcnow()
        db.session.add(contact)
        db.session.commit()


# use ethplorer to fetch eth balance & token holdings
def fetch_from_ethplorer():

    contacts = get_some_contacts()

    for contact in contacts:

        print("Fetching tokens & ETH balance for {}".format(contact.address))

        try:

            url = "http://api.ethplorer.io/getAddressInfo/%s" % (contact.address)
            results = call_ethplorer(url)

            contact.eth_balance = results["ETH"]["balance"]
            contact.transaction_count = results["countTxs"]

            if "tokens" in results:
                contact.tokens = results["tokens"]
                # update the OGN & DAI balance
                for token in results["tokens"]:
                    if token["tokenInfo"]["address"].lower() == token_stats.ogn_contract:
                        contact.ogn_balance = float(token["balance"]) / math.pow(10, 18)
                    elif token["tokenInfo"]["address"].lower() == token_stats.dai_contract:
                        contact.dai_balance = float(token["balance"]) / math.pow(10, 18)
                contact.token_count = len(results["tokens"])
            contact.last_updated = datetime.utcnow()

            db.session.add(contact)
            db.session.commit()

        except Exception as e:
            print(e)
            time.sleep(1)
            print("retrying")


# monitor & alert on all movement of OGN
def fetch_ogn_transactions():

    etherscan_url = (
        "http://api.etherscan.io/api?module=account&action=tokentx&contractaddress=%s&startblock=0&endblock=999999999&sort=desc&apikey=%s"
        % (token_stats.ogn_contract, constants.ETHERSCAN_KEY)
    )
    # print(etherscan_url)
    results = call_etherscan(etherscan_url)

    # loop through every transaction where Origin tokens were moved
    for result in results["result"]:
        tx = db_common.get_or_create(
            db.session, db_models.TokenTransaction, tx_hash=result["hash"]
        )
        tx.from_address = result["from"].lower()
        tx.to_address = result["to"].lower()
        # intentionally using ETH instead of WEI to be more human-friendly, despite being less precise
        tx.amount = float(result["value"]) / math.pow(10, 18)
        tx.block_number = result["blockNumber"]
        tx.timestamp = time_.fromtimestamp(result["timeStamp"])

        if tx.amount > 0:
            print("%g OGN moved in transaction {}".format(tx.amount, result["hash"]))

        # send an email alert every time OGN tokens are moved
        # only alert once & ignore marketplace transactions which show up as 0 OGN
        if tx.amount > 1000 and not tx.notification_sent:
            to_details = lookup_details(tx.to_address)
            from_details = lookup_details(tx.from_address)

            if from_details.name and to_details.name:
                subject = "%s moved %g OGN to %s" % (
                    from_details.name,
                    tx.amount,
                    to_details.name,
                )
            elif from_details.name:
                subject = "%s moved %g OGN" % (from_details.name, tx.amount)
            elif to_details.name:
                subject = "%g OGN moved to %s" % (tx.amount, to_details.name)
            else:
                subject = "%g OGN moved" % (tx.amount)

            body = u"""
                {amount} OGN <a href='https://etherscan.io/tx/{tx_hash}'>moved</a>
                from <a href='https://etherscan.io/address/{from_address}'>{from_name}</a>
                to <a href='https://etherscan.io/address/{to_address}'>{to_name}</a>
            """.format(
                amount="{0:g}".format(float(tx.amount)),
                tx_hash=tx.tx_hash,
                from_name=from_details.name if from_details.name else tx.from_address,
                from_address=tx.from_address,
                to_name=to_details.name if to_details.name else tx.to_address,
                to_address=tx.to_address,
            )

            print(subject)

            sgw.notify_founders(body, subject)
            tx.notification_sent = True
            db.session.add(tx)
            db.session.commit()

# Fetches OGN contract token info
def fetch_ogn_token_info():
    print("Checking OGN token info")

    url = "http://api.ethplorer.io/getTokenInfo/%s" % (token_stats.ogn_contract)
    results = call_ethplorer(url)

    if "error" in results:
        print("Error while fetching token info")
        print(results["error"]["message"])
        raise ValueError(results["error"]["message"])

    token_info = db_common.get_or_create(
        db.session, db_models.TokenInfo
    )

    token_info.total_supply = results["totalSupply"]
    token_info.holders = results["holdersCount"]
    token_info.transfers_count = results["transfersCount"]

    db.session.add(token_info)
    db.session.commit()

    return token_info


# Fetches wallet balance from API and stores that to DB
def fetch_wallet_balance(wallet):
    print("Checking the balance of wallet {}".format(
        wallet,
    ))

    url = "http://api.ethplorer.io/getAddressInfo/%s" % (wallet)
    results = call_ethplorer(url)

    contact = db_common.get_or_create(
        db.session, db_models.EthContact, address=wallet
    )

    if "error" in results:
        print("Error while fetching balance")
        print(results["error"]["message"])
        raise ValueError(results["error"]["message"])

    contact.eth_balance = results["ETH"]["balance"]
    contact.transaction_count = results["countTxs"]

    print("ETH balance of {} is {}".format(wallet, results["ETH"]["balance"]))
    if "tokens" in results:
        contact.tokens = results["tokens"]
        # update the OGN & DAI balance
        for token in results["tokens"]:
            if token["tokenInfo"]["address"] == token_stats.ogn_contract:
                contact.ogn_balance = float(token["balance"]) / math.pow(10, 18)
                print("OGN balance of {} is {}".format(wallet, contact.ogn_balance))
            elif token["tokenInfo"]["address"] == token_stats.dai_contract:
                contact.dai_balance = float(token["balance"]) / math.pow(10, 18)
                print("DAI balance of %s is %s".format(wallet, contact.dai_balance))
        contact.token_count = len(results["tokens"])
    contact.last_updated = datetime.utcnow()

    db.session.add(contact)
    db.session.commit()

    return contact

# alerting system to notify us if a wallet drops below a certain threshold
def alert_on_balance_drop(wallet, label, eth_threshold):

    print("Checking if the balance of {} ({}) is below {}".format(
        wallet,
        label,
        eth_threshold,
    ))

    try:
        contact  = fetch_wallet_balance(wallet)

        print(contact.eth_balance)

        if contact.eth_balance < eth_threshold:
            print("Low balance. Notifying.")
            subject = "%s purse is running low. %s ETH remaining" % (
                label,
                contact.eth_balance,
            )
            body = "Please send more ETH to %s" % (wallet)
            print(body)
            print(subject)
            sgw.notify_founders(body, subject)

    except Exception as e:
        print(e)

# Fetch reserved wallet balance
def fetch_reserved_wallet_balances():
    print("Computing OGN stats...")
    # Fetch reserved wallet balances
    fetch_wallet_balance(token_stats.foundation_reserve_address)
    fetch_wallet_balance(token_stats.team_dist_address)
    fetch_wallet_balance(token_stats.investor_dist_address)
    fetch_wallet_balance(token_stats.dist_staging_address)
    fetch_wallet_balance(token_stats.partnerships_address)
    fetch_wallet_balance(token_stats.ecosystem_growth_address)
    fetch_wallet_balance(token_stats.ogn_staking_contract)

if __name__ == "__main__":
    # called via cron on Heroku
    with db_utils.request_context():
        # fetch_ogn_transactions()
        # alert_on_balance_drop("0x440EC5490c26c58A3c794f949345b10b7c83bdC2", "AC", 1)
        # alert_on_balance_drop("0x5fabfc823e13de8f1d138953255dd020e2b3ded0", "Meta-transactions", 1)
        alert_on_balance_drop("0xDF73aF150b8E446a6D39FDdc2CFA7Bf067B88936", "Dshop", 1)
        # fetch token info
        fetch_ogn_token_info()
        # fetch_from_ethplorer()
        fetch_reserved_wallet_balances()

        token_stats.compute_ogn_stats()
