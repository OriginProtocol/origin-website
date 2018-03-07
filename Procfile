web: newrelic-admin run-program gunicorn main:app
init: python tools/manage.py db init
migrate: python tools/manage.py db migrate
upgrade: python tools/manage.py db upgrade
stamph: python tools/manage.py db stamp head
worker: celery -A util.tasks worker
fcsync: python util/backfills.py
testfcsync: python util/backfills -l 100
