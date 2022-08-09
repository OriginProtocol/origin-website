import argparse
import collections

from database import db, db_models, db_common
from tools import db_utils
from datetime import datetime
from config import constants

import math
import requests
from util import time_

from sqlalchemy import or_, and_, func

# ogn wallet addresses
foundation_reserve_address = "0xe011fa2a6df98c69383457d87a056ed0103aa352"
team_dist_address = "0xcaa5ef7abc36d5e5a3e4d7930dcff3226617a167"
investor_dist_address = "0x3da5045699802ea1fcc60130dedea67139c5b8c0"
dist_staging_address = "0x1a34e5b97d684b124e32bd3b7dc82736c216976b"
partnerships_address = "0xbc0722eb6e8ba0217aeea5694fe4f214d2e53017"
ecosystem_growth_address = "0x2d00c3c132a0567bbbb45ffcfd8c6543e08ff626"

reserved_addresses = (
  foundation_reserve_address,
  team_dist_address,
  investor_dist_address,
  dist_staging_address,
  partnerships_address,
  ecosystem_growth_address,
)

ogn_contract = "0x8207c1ffc5b6804f6024322ccf34f29c3541ae26"

def insert_data(snapshot_date, supply, do_it):
  if not do_it:
    print("Will set supply of month {} to {}".format(snapshot_date, supply))
    return

  instance = db_models.CirculatingOgnSupply(
    supply_amount=supply,
    snapshot_date=snapshot_date
  )

  db.session.add(instance)

def delete_bad_data(do_it):
  if not do_it:
    bad_data_result = db.engine.execute("""
    select count(*) from circulating_supply where snapshot_date >= '2020-06-01'::date and snapshot_date <= '2020-06-15'::date
    """)
    print("Skipping delete statement that'd delete {} records".format(list(bad_data_result)[0][0]))
    return
  db.engine.execute("""
  delete from circulating_supply where snapshot_date >= '2020-06-01'::date and snapshot_date <= '2020-06-15'::date
  """)

def fill_missing_txs(do_it):
  start_block = 10176690
  new_supply = 58821352

  etherscan_url = (
    "http://api.etherscan.io/api?module=account&action=tokentx&contractaddress=%s&startblock=%s&endblock=999999999&sort=asc&apikey=%s"
    % (ogn_contract, start_block, constants.ETHERSCAN_KEY)
  )

  raw_json = requests.get(etherscan_url)
  results = raw_json.json()
  update = 0

  for result in results["result"]:
    from_address = result["from"].lower()
    to_address = result["to"].lower()
    amount = float(result["value"]) / math.pow(10, 18)
    if from_address in reserved_addresses and to_address not in reserved_addresses:
      new_supply = new_supply + amount
    elif from_address not in reserved_addresses and to_address in reserved_addresses:
      new_supply = new_supply - amount
    else:
      continue
  
    update = update + 1
    instance = db_common.get_or_create(
      db.session, db_models.CirculatingOgnSupply, snapshot_date=time_.fromtimestamp(result["timeStamp"])
    )
    instance.supply_amount = new_supply
    db.session.add(instance)

    print("{} {}".format(time_.fromtimestamp(result["timeStamp"]), new_supply))
  
  if do_it:
    db.session.commit()

  print("Have parsed {}/{} transactions".format(update, len(results["result"])))
  print("Circulating supply at the end of all txs: {}".format(new_supply))

def main(do_it):
  delete_bad_data(do_it)
  fill_missing_txs(do_it)

if __name__ == '__main__':
  with db_utils.request_context():
    parser = argparse.ArgumentParser()
    parser.add_argument('--do_it', action='store_true')
    args = parser.parse_args()
    main(args.do_it)
