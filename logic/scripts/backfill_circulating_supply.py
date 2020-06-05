import argparse
import collections

from database import db, db_models, db_common
from tools import db_utils
from datetime import datetime

def insert_data(month, supply, do_it):
  if not do_it:
    print "Will set supply of month %s to %s" % (month, supply)
    return

  instance = db_models.CirculatingSupply(
    supply_amount=supply,
    snapshot_date=datetime.utcnow().replace(
      year=2020,
      month=month,
      day=1,
      hour=0,
      minute=0,
      second=0, 
      microsecond=0
    )
  )

  db.session.add(instance)


def main(do_it):
    print('Starting backfill...')

    # data from blockchain
    jan_supply = 23408605
    feb_supply = 28334082
    mar_supply = 28573260
    apr_supply = 33523317
    may_supply = 55558189

    insert_data(month=1, supply=jan_supply, do_it=do_it)
    insert_data(month=2, supply=feb_supply, do_it=do_it)
    insert_data(month=3, supply=mar_supply, do_it=do_it)
    insert_data(month=4, supply=apr_supply, do_it=do_it)
    insert_data(month=5, supply=may_supply, do_it=do_it)

    db.session.commit()

    print("Circulating supply has been backfilled.")

if __name__ == '__main__':
  with db_utils.request_context():
    parser = argparse.ArgumentParser()
    parser.add_argument('--do_it', action='store_true')
    args = parser.parse_args()
    main(args.do_it)
