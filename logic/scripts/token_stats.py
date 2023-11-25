import collections
from datetime import datetime, timedelta
import dateutil.parser
import json
import math
import os
import timeago

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
ogv_contract = "0x9c354503c38481a7a7a51629142963f98ecc12d0"
ousd_contract = "0x2a8e1e676ec238d8a992307b495b45b3feaa5e86"
oeth_contract = "0x856c4efb76c1d1ae02e20ceb03a2a6a08b0b8dc3"
dai_contract = "0x89d24a6b4ccb1b6faa2625fe562bdd9a23260359"
ogn_staking_contract = "0x501804b374ef06fa9c427476147ac09f1551b9a0"

# ogn wallet addresses
foundation_reserve_address = "0xe011fa2a6df98c69383457d87a056ed0103aa352"
new_foundation_reserve_address = "0xbe2ab3d3d8f6a32b96414ebbd865dbd276d3d899"
team_dist_address = "0xcaa5ef7abc36d5e5a3e4d7930dcff3226617a167"
new_team_dist_address = "0x2eae0cae2323167abf78462e0c0686865c67a655"
investor_dist_address = "0x3da5045699802ea1fcc60130dedea67139c5b8c0"
new_investor_dist_address = "0xfe730b3cf80ca7b31905f70241f7c786baf443e3"
dist_staging_address = "0x1a34e5b97d684b124e32bd3b7dc82736c216976b"
new_dist_staging_address = "0x12d7ef3c933d091210cd931224ead45d9cfddde0"
partnerships_address = "0xbc0722eb6e8ba0217aeea5694fe4f214d2e53017"
ecosystem_growth_address = "0x2d00c3c132a0567bbbb45ffcfd8c6543e08ff626"
staked_ogv_address = "0x0c4576ca1c365868e162554af8e385dc3e7c66d9"
ogv_claims_address = "0x7ae2334f12a449895ad21d4c255d9de194fe986f"
veogv_claims_address = "0xd667091c2d1dcc8620f4eaea254cdfb0a176718d"
brave_endeavors_address = "0x8ac3b96d118288427055ae7f62e407fc7c482f57"
limitless_alpha_address = "0xa2cc2eae69cbf04a3d5660bc3e689b035324fc3f"

# Fetches and stores OGN & ETH prices froom CoinGecko
def fetch_token_prices():
    print("Fetching token prices...")
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=origin-protocol%2Corigin-dollar-governance%2Cethereum&vs_currencies=usd"
        raw_json = requests.get(url)
        response = raw_json.json()

        if "error" in response:
            print("Error while fetching balance")
            print(response["error"]["message"])
            raise ValueError(response["error"]["message"])

        ogn_usd_price = float(response["origin-protocol"]["usd"] or 0)
        ogv_usd_price = float(response["origin-dollar-governance"]["usd"] or 0)
        eth_usd_price = float(response["ethereum"]["usd"] or 0)

        print("Set OGN price to {}".format(ogn_usd_price))
        print("Set OGV price to {}".format(ogv_usd_price))
        print("Set ETH price to {}".format(eth_usd_price))

        return dict([
            ("ogn_usd_price", ogn_usd_price),
            ("ogv_usd_price", ogv_usd_price),
            ("eth_usd_price", eth_usd_price)
        ])

    except Exception as e:
        print("Failed to load token prices")
        print(e)

def fetch_stats_from_t3(investor_portal = True):
    print("Fetching T3 stats...")

    url = "https://remote.team.originprotocol.com/api/user-stats"

    if investor_portal:
        url = "https://remote.investor.originprotocol.com/api/user-stats"

    raw_json = requests.get(url)
    response = raw_json.json()

    return response

def fetch_onchain_staking_stats():
    print("Fetching on-chain OGN staking stats...")

    url =  "https://analytics.ousd.com/api/v1/staking_stats"

    raw_json = requests.get(url)
    response = raw_json.json()

    return response

def fetch_onchain_staking_stats_by_duration():
    print("Fetching on-chain OGN staking stats...")

    url = "https://analytics.ousd.com/api/v1/staking_stats_by_duration"
    raw_json = requests.get(url)
    response = raw_json.json()
    return response

def fetch_staking_stats():
    print("Fetching T3 and on-chain OGN staking stats...")

    sum_users = 0
    sum_tokens = 0

    ogn_stakers_count = 0
    ogn_staked_amount = 0

    try:
        investor_stats = fetch_stats_from_t3(investor_portal=True)
        team_stats = fetch_stats_from_t3(investor_portal=False)
        staking_stats = fetch_onchain_staking_stats()

        investor_staked_users = int(investor_stats["userCount"] or 0)
        investor_locked_sum = int(math.ceil(float(investor_stats["lockupSum"] or 0)))

        team_staked_users = int(team_stats["userCount"] or 0)
        team_locked_sum = int(math.ceil(float(team_stats["lockupSum"] or 0)))

        ogn_stakers_count = int(staking_stats["userCount"] or 0)
        ogn_staked_amount = int(math.ceil(float(staking_stats["lockupSum"] or 0)))

        sum_users = investor_staked_users + team_staked_users
        sum_tokens = investor_locked_sum + team_locked_sum

        print("There are {} users and {} locked up tokens".format(sum_users, sum_tokens))

    except Exception as e:
        print("Failed to load user stats")
        print(e)

    return dict([
        ("staked_user_count", sum_users),
        ("staked_token_count", sum_tokens),
        ("ogn_stakers_count", ogn_stakers_count),
        ("ogn_staked_amount", ogn_staked_amount)
    ])

def total_supply(address):
    url = "https://api.etherscan.io/api?module=stats&action=tokensupply&contractaddress=%s&apikey=%s" % (address, constants.ETHERSCAN_KEY)
    response = requests.get(url)
    wei = response.json()["result"]
    return wei[:-18]

def total_ogn():
    return total_supply(ogn_contract)

def total_ogv():
    return total_supply(ogv_contract)

def total_ousd():
    return total_supply(ousd_contract)

def total_oeth():
    return total_supply(oeth_contract)

def fetch_ogn_stats(ogn_usd_price,staked_user_count,staked_token_count,ogn_stakers_count,ogn_staked_amount):
    total_supply = int(total_ogn())

    number_of_addresses = db_models.TokenInfo.query.order_by(
        db_models.TokenInfo.created_at.desc()
    ).first().holders

    results = db_models.EthContact.query.filter(db_models.EthContact.address.in_((
        foundation_reserve_address,
        new_foundation_reserve_address,
        team_dist_address,
        new_team_dist_address,
        investor_dist_address,
        new_investor_dist_address,
        dist_staging_address,
        new_dist_staging_address,
        partnerships_address,
        ecosystem_growth_address,
        brave_endeavors_address,
        limitless_alpha_address
    ))).all()

    ogn_balances = dict([(result.address, result.ogn_balance) for result in results])

    foundation_reserve_balance = int(ogn_balances[foundation_reserve_address])
    new_foundation_reserve_balance = int(ogn_balances[new_foundation_reserve_address])
    team_dist_balance = int(ogn_balances[team_dist_address])
    new_team_dist_balance = int(ogn_balances[new_team_dist_address])
    investor_dist_balance = int(ogn_balances[investor_dist_address])
    new_investor_dist_balance = int(ogn_balances[new_investor_dist_address])
    dist_staging_balance = int(ogn_balances[dist_staging_address])
    new_dist_staging_balance = int(ogn_balances[new_dist_staging_address])
    partnerships_balance = int(ogn_balances[partnerships_address])
    ecosystem_growth_balance = int(ogn_balances[ecosystem_growth_address])
    brave_endeavors_balance = int(ogn_balances[brave_endeavors_address])
    limitless_alpha_balance = int(ogn_balances[limitless_alpha_address])
    
    reserved_tokens = int(
        foundation_reserve_balance +
        new_foundation_reserve_balance + 
        team_dist_balance +
        new_team_dist_balance +
        investor_dist_balance +
        new_investor_dist_balance +
        dist_staging_balance +
        new_dist_staging_balance +
        partnerships_balance +
        ecosystem_growth_balance + 
        brave_endeavors_balance +
        limitless_alpha_balance
    )
    
    print("Full reserved token balance: {}".format(reserved_tokens))
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

        ("ogn_stakers_count", ogn_stakers_count),
        ("ogn_staked_amount", ogn_staked_amount),

        ("foundation_reserve_address", foundation_reserve_address),
        ("new_foundation_reserve_address", new_foundation_reserve_address),
        ("team_dist_address", team_dist_address),
        ("new_team_dist_address", new_team_dist_address),
        ("investor_dist_address", investor_dist_address),
        ("new_investor_dist_address", new_investor_dist_address),
        ("dist_staging_address", dist_staging_address),
        ("new_dist_staging_address", new_dist_staging_address),
        ("partnerships_address", partnerships_address),
        ("ecosystem_growth_address", ecosystem_growth_address),

        # formatted wallet balances
        ("foundation_reserve_balance_formatted", '{:,}'.format(foundation_reserve_balance)),
        ("new_foundation_reserve_balance_formatted", '{:,}'.format(new_foundation_reserve_balance)),
        ("team_dist_balance_formatted", '{:,}'.format(team_dist_balance)),
        ("new_team_dist_balance_formatted", '{:,}'.format(new_team_dist_balance)),
        ("investor_dist_balance_formatted", '{:,}'.format(investor_dist_balance)),
        ("new_investor_dist_balance_formatted", '{:,}'.format(new_investor_dist_balance)),
        ("dist_staging_balance_formatted", '{:,}'.format(dist_staging_balance)),
        ("new_dist_staging_balance_formatted", '{:,}'.format(new_dist_staging_balance)),
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
        ("formatted_ogn_staked_amount", '{:,}'.format(ogn_staked_amount)),
        ("created_at_formatted", datetime.utcnow().strftime("%m/%d/%Y %-I:%M:%S %p")),
        ("created_at_iso", datetime.utcnow().isoformat()),
    ])

    return out_data

def fetch_ogv_stats(ogv_usd_price):
    total_supply = int(total_ogv())

    results = db_models.EthContact.query.filter(db_models.EthContact.address.in_((
        new_foundation_reserve_address,
        team_dist_address,
        new_team_dist_address,
        investor_dist_address,
        new_investor_dist_address,
        new_dist_staging_address,
        staked_ogv_address,
        ogv_claims_address,
        veogv_claims_address,
        brave_endeavors_address,
        limitless_alpha_address,
    ))).all()

    ogv_balances = dict([(result.address, result.ogv_balance) for result in results])

    new_foundation_reserve_balance = int(ogv_balances[new_foundation_reserve_address])
    team_dist_balance = int(ogv_balances[team_dist_address])
    new_team_dist_balance = int(ogv_balances[new_team_dist_address])
    investor_dist_balance = int(ogv_balances[investor_dist_address])
    new_investor_dist_balance = int(ogv_balances[new_investor_dist_address])
    new_dist_staging_balance = int(ogv_balances[new_dist_staging_address])
    staked_ogv_balance = int(ogv_balances[staked_ogv_address])
    ogv_claims_balance = int(ogv_balances[ogv_claims_address])
    veogv_claims_balance = int(ogv_balances[veogv_claims_address])
    brave_endeavors_balance = int(ogv_balances[brave_endeavors_address])
    limitless_alpha_balance = int(ogv_balances[limitless_alpha_address])
    
    reserved_tokens = int(
        new_foundation_reserve_balance + 
        team_dist_balance +
        new_team_dist_balance +
        investor_dist_balance +
        new_investor_dist_balance +
        new_dist_staging_balance +
        staked_ogv_balance +
        ogv_claims_balance +
        veogv_claims_balance +
        brave_endeavors_balance +
        limitless_alpha_balance
    )
    
    print("Full reserved token balance: {}".format(reserved_tokens))
    circulating_supply = int(total_supply - reserved_tokens)

    market_cap = int(circulating_supply * ogv_usd_price)

    out_data = dict([
        ("ogv_usd_price", ogv_usd_price),
        ("circulating_supply", circulating_supply),
        ("market_cap", market_cap),
        ("total_supply", total_supply),

        ("reserved_tokens", reserved_tokens),

        ("new_foundation_reserve_address", new_foundation_reserve_address),
        ("team_dist_address", team_dist_address),
        ("new_team_dist_address", new_team_dist_address),
        ("investor_dist_address", investor_dist_address),
        ("new_investor_dist_address", new_investor_dist_address),
        ("new_dist_staging_address", new_dist_staging_address),
        ("staked_ogv_address", staked_ogv_address),
        ("ogv_claims_address", ogv_claims_address),
        ("veogv_claims_address", veogv_claims_address),
        ("brave_endeavors_address", brave_endeavors_address),
        ("limitless_alpha_address", limitless_alpha_address),

        # formatted wallet balances
        ("new_foundation_reserve_balance_formatted", '{:,}'.format(new_foundation_reserve_balance)),
        ("team_dist_balance_formatted", '{:,}'.format(team_dist_balance)),
        ("new_team_dist_balance_formatted", '{:,}'.format(new_team_dist_balance)),
        ("investor_dist_balance_formatted", '{:,}'.format(investor_dist_balance)),
        ("new_investor_dist_balance_formatted", '{:,}'.format(new_investor_dist_balance)),
        ("new_dist_staging_balance_formatted", '{:,}'.format(new_dist_staging_balance)),
        ("staked_ogv_balance_formatted", '{:,}'.format(staked_ogv_balance)),
        ("ogv_claims_balance_formatted", '{:,}'.format(ogv_claims_balance)),
        ("veogv_claims_balance_formatted", '{:,}'.format(veogv_claims_balance)),
        ("breave_endeavors_balance_formatted", '{:,}'.format(brave_endeavors_balance)),
        ("limitless_alpha_balance_formatted", '{:,}'.format(limitless_alpha_balance)),

        # Formatted values to display
        ("formatted_ogv_usd_price", '${:,}'.format(ogv_usd_price)),
        ("formatted_circulating_supply", '{:,}'.format(circulating_supply)),
        ("formatted_market_cap", '${:,}'.format(market_cap)),
        ("formatted_total_supply", '{:,}'.format(total_supply)),
        ("formatted_reserved_tokens", '{:,}'.format(reserved_tokens)),
        ("created_at_formatted", datetime.utcnow().strftime("%m/%d/%Y %-I:%M:%S %p")),
        ("created_at_iso", datetime.utcnow().isoformat()),
    ])

    return out_data

def update_ogn_circulating_supply(circulating_supply):
    snapshot_date = datetime.utcnow()

    supply_snapshot = db_common.get_or_create(
        db.session, db_models.CirculatingOgnSupply, snapshot_date=snapshot_date
    )

    supply_snapshot.supply_amount = circulating_supply
    db.session.commit()

    supply_data = db.engine.execute("""
    select timewin, max(s.supply_amount)
    from 
        generate_series(now() - interval '12 month', now(), '1 day') as timewin
    left outer join 
        (select * from circulating_ogn_supply where snapshot_date > now() - interval '12 month' and snapshot_date > '2020-01-01'::date order by snapshot_date desc) s
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

    print("Updated current OGN circulating supply to {}".format(circulating_supply))

    return out

def update_ogv_circulating_supply(circulating_supply):
    snapshot_date = datetime.utcnow()

    supply_snapshot = db_common.get_or_create(
        db.session, db_models.CirculatingOgvSupply, snapshot_date=snapshot_date
    )

    supply_snapshot.supply_amount = circulating_supply
    db.session.commit()

    supply_data = db.engine.execute("""
    select timewin, max(s.supply_amount)
    from 
        generate_series(now() - interval '12 month', now(), '1 day') as timewin
    left outer join 
        (select * from circulating_ogv_supply where snapshot_date > now() - interval '12 month' and snapshot_date > '2020-01-01'::date order by snapshot_date desc) s
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

    print("Updated current OGV circulating supply to {}".format(circulating_supply))

    return out

def get_ogn_stats():
    redis_client = redis_helper.get_redis_client()

    stats = json.loads(redis_client.get("ogn_stats") or "{}")
    stats["ogn_supply_stats"]["created_at_formatted_timeago"] = stats["ogn_supply_stats"]["created_at_formatted"]

    if "created_at_iso" in stats["ogn_supply_stats"]:
        stats["ogn_supply_stats"]["created_at_formatted_timeago"] = timeago.format(dateutil.parser.parse(stats["ogn_supply_stats"]["created_at_iso"]), datetime.utcnow())

    return stats

def get_ogv_stats():
    redis_client = redis_helper.get_redis_client()

    stats = json.loads(redis_client.get("ogv_stats") or "{}")
    stats["ogv_supply_stats"]["created_at_formatted_timeago"] = stats["ogv_supply_stats"]["created_at_formatted"]

    if "created_at_iso" in stats["ogv_supply_stats"]:
        stats["ogv_supply_stats"]["created_at_formatted_timeago"] = timeago.format(dateutil.parser.parse(stats["ogv_supply_stats"]["created_at_iso"]), datetime.utcnow())

    return stats

# Fetches reserved wallet balances and token price 
# and recalculates things to be shown in
def compute_ogn_stats():
    print("Computing OGN stats...")

    # Fetch OGN and ETH prices
    token_prices = fetch_token_prices()

    staking_stats = fetch_staking_stats()

    ogn_staked_data = fetch_onchain_staking_stats_by_duration()

    ogn_supply_stats = fetch_ogn_stats(
        token_prices["ogn_usd_price"], 
        staking_stats["staked_user_count"], 
        staking_stats["staked_token_count"],
        staking_stats["ogn_stakers_count"],
        staking_stats["ogn_staked_amount"]
    )

    ogn_supply_history = update_ogn_circulating_supply(ogn_supply_stats["circulating_supply"])

    redis_client = redis_helper.get_redis_client()
    redis_client.set("ogn_stats", json.dumps(
        dict([
            ("ogn_supply_stats", ogn_supply_stats),
            ("ogn_staked_data", json.dumps(ogn_staked_data["data"])),
            ("ogn_supply_history", json.dumps(ogn_supply_history))
        ])
    ))

def compute_ogv_stats():
    print("Computing OGV stats...")

    token_prices = fetch_token_prices()

    ogv_supply_stats = fetch_ogv_stats(
        token_prices["ogv_usd_price"]
    )

    ogv_supply_history = update_ogv_circulating_supply(ogv_supply_stats["circulating_supply"])

    redis_client = redis_helper.get_redis_client()
    redis_client.set("ogv_stats", json.dumps(
        dict([
            ("ogv_supply_stats", ogv_supply_stats)
        ])
    ))

if __name__ == "__main__":
    with db_utils.request_context():
        compute_ogn_stats()
        compute_ogv_stats()
