web: bin/start-nginx gunicorn -c ./config/gunicorn.conf.py main:app
init: python tools/manage.py db init
migrate: python tools/manage.py db migrate
upgrade: python tools/manage.py db upgrade
stamph: python tools/manage.py db stamp head
worker: celery -A util.tasks worker
