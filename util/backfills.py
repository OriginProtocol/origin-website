import os
from app import app_config
from config import constants

from database import db, db_common, db_models

#from app import app_config
from flask import Flask
from itertools import izip_longest
from tasks import full_contact_request
import pdb

from logic.emails import email_types

flask_app = Flask(__name__)

flask_app.config.update(
    broker_url=os.environ['REDIS_URL'],
    result_backend=os.environ['REDIS_URL'],
    task_always_eager=os.environ.get('CELERY_DEBUG', False)
)

app_config.init_prod_app(flask_app)

def backfill_presale():
    with flask_app.app_context():
        # todo limit parsing
        LIMIT = 100000
        UNFILLED = """
            SELECT DISTINCT presale.email
            FROM presale
                LEFT JOIN fullcontact ON presale.email = fullcontact.email
            WHERE fullcontact.id IS NULL
        """
        result = db.engine.execute(UNFILLED)

        # grouping
        for row in result:
            print row
            full_contact_request(row[0])

backfill_presale()
