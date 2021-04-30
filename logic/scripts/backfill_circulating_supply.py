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

  instance = db_models.CirculatingSupply(
    supply_amount=supply,
    snapshot_date=snapshot_date
  )

  db.session.add(instance)

def fill_missing_txs(do_it):
  # last_tx_db = db_models.TokenTransaction.query.order_by(
  #   db_models.TokenTransaction.block_number.desc()
  # ).first()

  last_entry = db_models.CirculatingSupply.query.order_by(
    db_models.CirculatingSupply.snapshot_date.desc()
  ).first()

  if not last_entry:
    print("Couldn't find any entry on DB")
    return

  start_block = 10178155 # the last one in DB, same as last_tx_db.block_number
  new_supply = last_entry.supply_amount

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
      db.session, db_models.CirculatingSupply, snapshot_date=time_.fromtimestamp(result["timeStamp"])
    )
    instance.supply_amount = new_supply
    db.session.add(instance)
  
  if do_it:
    db.session.commit()

  print("Have parsed {} transactions".format(update))
  print("Circulating supply at the end of all txs: {}".format(new_supply))

def fill_from_token_tx(start_block, current_supply, do_it):
  print("Fetching TokenTransaction data from DB...")

  txs = db_models.TokenTransaction.query.order_by(
    db_models.TokenTransaction.block_number.asc(),
    db_models.TokenTransaction.timestamp.asc()
  ).filter(
    and_(
      db_models.TokenTransaction.block_number > start_block,
      or_(
        db_models.TokenTransaction.from_address.in_(reserved_addresses),
        db_models.TokenTransaction.to_address.in_(reserved_addresses),
      )
    )
  ).all()

  new_supply = current_supply
  update = 0
  for tx in txs:
    if tx.from_address in reserved_addresses and tx.to_address not in reserved_addresses:
      new_supply = new_supply + tx.amount
    elif tx.from_address not in reserved_addresses and tx.to_address in reserved_addresses:
      new_supply = new_supply - tx.amount
    else:
      continue
    update = update + 1
    insert_data(tx.timestamp, new_supply, do_it)

  if do_it:
    db.session.commit()

  print("Have updated {} records".format(update))
  print("Circulating supply at the end of the DB data: {}".format(new_supply))

def main(do_it):
  start_block = 9193265
  current_supply = 1224981 # Supply as on block 9193265 (Jan 1, 2020)

  fill_from_token_tx(start_block, current_supply, do_it)

  fill_missing_txs(do_it)

if __name__ == '__main__':
  with db_utils.request_context():
    parser = argparse.ArgumentParser()
    parser.add_argument('--do_it', action='store_true')
    args = parser.parse_args()
    main(args.do_it)
