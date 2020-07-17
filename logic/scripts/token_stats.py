import collections
from datetime import datetime, timedelta
import json
import math
import os

from config import constants
from database import db, db_models, db_common
from ratelimit import limits, sleep_and_retry, RateLimitException
import requests

from threading import Thread
from time import sleep

from tools import db_utils
from util import redis_helper
import json

# NOTE: remember to use lowercase addresses for everything

# token contract addresses
ogn_contract = "0x8207c1ffc5b6804f6024322ccf34f29c3541ae26"
dai_contract = "0x89d24a6b4ccb1b6faa2625fe562bdd9a23260359"

# ogn wallet addresses
foundation_reserve_address = "0xe011fa2a6df98c69383457d87a056ed0103aa352"
team_dist_address = "0xcaa5ef7abc36d5e5a3e4d7930dcff3226617a167"
investor_dist_address = "0x3da5045699802ea1fcc60130dedea67139c5b8c0"
dist_staging_address = "0x1a34e5b97d684b124e32bd3b7dc82736c216976b"
partnerships_address = "0xbc0722eb6e8ba0217aeea5694fe4f214d2e53017"
ecosystem_growth_address = "0x2d00c3c132a0567bbbb45ffcfd8c6543e08ff626"

# limit calls to 10 requests / second per their limits
# https://github.com/EverexIO/Ethplorer/wiki/Ethplorer-API#api-keys-limits
@sleep_and_retry
@limits(calls=10, period=1)
def call_ethplorer(url):
    url = "%s?apiKey=%s" % (url, constants.ETHPLORER_KEY)
    raw_json = requests.get(url)
    return raw_json.json()


# Fetches wallet balance from API and stores that to DB
def fetch_wallet_balance(wallet):
    print "Checking the balance of wallet %s" % (
        wallet,
    )

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

    print "ETH balance of %s is %s" % (wallet, results["ETH"]["balance"])
    if "tokens" in results:
        contact.tokens = results["tokens"]
        # update the OGN & DAI balance
        for token in results["tokens"]:
            if token["tokenInfo"]["address"] == ogn_contract:
                contact.ogn_balance = float(token["balance"]) / math.pow(10, 18)
            elif token["tokenInfo"]["address"] == dai_contract:
                contact.dai_balance = float(token["balance"]) / math.pow(10, 18)
        contact.token_count = len(results["tokens"])
    contact.last_updated = datetime.utcnow()

    db.session.add(contact)
    db.session.commit()

    return contact

# Fetches and stores OGN & ETH prices froom CoinGecko
def fetch_token_prices():
    print("Fetching token prices...")

    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=origin-protocol%2Cethereum&vs_currencies=usd"
        raw_json = requests.get(url)
        response = raw_json.json()

        if "error" in response:
            print("Error while fetching balance")
            print(response["error"]["message"])
            raise ValueError(response["error"]["message"])

        ogn_usd_price = float(response["origin-protocol"]["usd"] or 0)
        eth_usd_price = float(response["ethereum"]["usd"] or 0)

        print "Set OGN price to %s" % ogn_usd_price
        print "Set ETH price to %s" % eth_usd_price

        return dict([
            ("ogn_usd_price", ogn_usd_price),
            ("eth_usd_price", eth_usd_price)
        ])

    except Exception as e:
        print("Failed to load token prices")
        print e

def fetch_stats_from_t3(investor_portal = True):
    print("Fetching T3 stats...")

    url = "https://remote.team.originprotocol.com/api/user-stats"

    if investor_portal:
        url = "https://remote.investor.originprotocol.com/api/user-stats"

    raw_json = requests.get(url)
    response = raw_json.json()

    return response

def fetch_stats_from_od():
    print("Fetching Origin Deals stats...")

    url = "https://origindeals.com/api/user/stats"

    raw_json = requests.get(url)
    response = raw_json.json()

    return response

def fetch_staking_stats():
    print("Fetching T3 and Origin Deals user stats...")

    sum_users = 0
    sum_tokens = 0

    try:
        investor_stats = fetch_stats_from_t3(investor_portal=True)
        team_stats = fetch_stats_from_t3(investor_portal=False)
        od_stats = fetch_stats_from_od()

        investor_staked_users = int(investor_stats["userCount"] or 0)
        investor_locked_sum = int(investor_stats["lockupSum"] or 0)

        team_staked_users = int(team_stats["userCount"] or 0)
        team_locked_sum = int(team_stats["lockupSum"] or 0)

        od_staked_users = int(od_stats["userCount"] or 0)
        od_locked_sum = int(od_stats["lockupSum"] or 0)

        sum_users = investor_staked_users + team_staked_users + od_staked_users
        sum_tokens = investor_locked_sum + team_locked_sum + od_locked_sum

        print "There are %s users and %s locked up tokens" % (sum_users, sum_tokens)

    except Exception as e:
        print("Failed to load user stats")
        print e

    return dict([
        ("staked_user_count", sum_users),
        ("staked_token_count", sum_tokens)
    ])

def fetch_ogn_stats(ogn_usd_price,staked_user_count,staked_token_count):
    total_supply = 1000000000

    ogn_usd_price
    staked_user_count
    staked_token_count

    number_of_addresses = db.session.query(db_models.EthContact.address).count()
    results = db_models.EthContact.query.filter(db_models.EthContact.address.in_((
        foundation_reserve_address,
        team_dist_address,
        investor_dist_address,
        dist_staging_address,
        partnerships_address,
        ecosystem_growth_address,
    ))).all()

    ogn_balances = dict([(result.address, result.ogn_balance) for result in results])

    foundation_reserve_balance = ogn_balances[foundation_reserve_address]
    team_dist_balance = ogn_balances[team_dist_address]
    investor_dist_balance = ogn_balances[investor_dist_address]
    dist_staging_balance = ogn_balances[dist_staging_address]
    partnerships_balance = ogn_balances[partnerships_address]
    ecosystem_growth_balance = ogn_balances[ecosystem_growth_address]
    
    reserved_tokens = int(
        foundation_reserve_balance +
        team_dist_balance +
        investor_dist_balance +
        dist_staging_balance +
        partnerships_balance +
        ecosystem_growth_balance 
    )
    
    print "Balances %s %s %s" % (foundation_reserve_balance, team_dist_balance, investor_dist_balance)
    circulating_supply = int(total_supply - reserved_tokens)

    market_cap = int(circulating_supply * ogn_usd_price)

    out_data = dict([
        ("ogn_usd_price", ogn_usd_price),
        ("circulating_supply", circulating_supply),
        ("market_cap", market_cap),
        ("total_supply", total_supply),
        ("number_of_addresses", number_of_addresses),
        ("number_of_addresses_formatted", '{:,}'.format(number_of_addresses)),

        ("reserved_tokens", reserved_tokens),
        ("staked_user_count", staked_user_count),
        ("staked_token_count", staked_token_count),

        ("foundation_reserve_address", foundation_reserve_address),
        ("team_dist_address", team_dist_address),
        ("investor_dist_address", investor_dist_address),
        ("dist_staging_address", dist_staging_address),
        ("partnerships_address", partnerships_address),
        ("ecosystem_growth_address", ecosystem_growth_address),

        # formatted wallet balances
        ("foundation_reserve_balance_formatted", '{:,}'.format(foundation_reserve_balance)),
        ("team_dist_balance_formatted", '{:,}'.format(team_dist_balance)),
        ("investor_dist_balance_formatted", '{:,}'.format(investor_dist_balance)),
        ("dist_staging_balance_formatted", '{:,}'.format(dist_staging_balance)),
        ("partnerships_balance_formatted", '{:,}'.format(partnerships_balance)),
        ("ecosystem_growth_balance_formatted", '{:,}'.format(ecosystem_growth_balance)),

        # Formatted values to display
        ("formatted_ogn_usd_price", '${:,}'.format(ogn_usd_price)),
        ("formatted_circulating_supply", '{:,}'.format(circulating_supply)),
        ("formatted_market_cap", '${:,}'.format(market_cap)),
        ("formatted_total_supply", '{:,}'.format(total_supply)),
        ("formatted_reserved_tokens", '{:,}'.format(reserved_tokens)),
        ("formatted_staked_user_count", '{:,}'.format(staked_user_count)),
        ("formatted_staked_token_count", '{:,}'.format(staked_token_count)),
        ("created_at_formatted", datetime.utcnow().strftime("%m/%d/%Y %-I:%M:%S %p"))
    ])

    return out_data

def update_circulating_supply(circulating_supply):
    snapshot_date = datetime.utcnow()

    supply_snapshot = db_common.get_or_create(
        db.session, db_models.CirculatingSupply, snapshot_date=snapshot_date
    )

    supply_snapshot.supply_amount = circulating_supply
    db.session.commit()

    supply_data = db.engine.execute("""
    select timewin, max(s.supply_amount)
    from 
        generate_series(now() - interval '12 month', now(), '1 day') as timewin
    left outer join 
        (select * from circulating_supply where snapshot_date > now() - interval '12 month' and snapshot_date > '2020-01-01'::date order by snapshot_date desc) s
    on s.snapshot_date < timewin 
        and s.snapshot_date >= timewin - (interval '1 day')
    where timewin > '2020-01-01'::date
    group by timewin
    order by timewin desc
    """)

    out = []

    supply_data_list = list(supply_data)
    latest_supply = supply_data_list[0][1]

    for row in supply_data_list:
        if row[1] is not None:
            latest_supply = row[1]

        out.append(dict([
            ("supply_amount", row[1] or latest_supply),
            ("snapshot_date", row[0].strftime("%Y/%m/%d %H:%M:%S"))
        ]))

    print "Updated current circulating supply to %s" % circulating_supply

    return out

def get_ogn_stats():
    redis_client = redis_helper.get_redis_client()

    return json.loads(redis_client.get("ogn_stats") or "{}")

# Fetches reserved wallet balances and token price 
# and recalculates things to be shown in
def compute_ogn_stats():
    print("Computing OGN stats...")

    # Fetch OGN and ETH prices
    token_prices = fetch_token_prices()

    staking_stats = fetch_staking_stats()

    ogn_supply_stats = fetch_ogn_stats(
        token_prices["ogn_usd_price"], 
        staking_stats["staked_user_count"], 
        staking_stats["staked_token_count"]
    )

    ogn_supply_history = update_circulating_supply(ogn_supply_stats["circulating_supply"])

    redis_client = redis_helper.get_redis_client()
    redis_client.set("ogn_stats", json.dumps(
        dict([
            ("ogn_supply_stats", ogn_supply_stats),
            ("ogn_supply_history", json.dumps(ogn_supply_history))
        ])
    ))

if __name__ == "__main__":
    with db_utils.request_context():
        compute_ogn_stats()
