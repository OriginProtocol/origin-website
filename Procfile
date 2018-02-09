web: newrelic-admin run-program gunicorn main:app
init: python manage.py db init
migrate: python manage.py db migrate
upgrade: python manage.py db upgrade
stamph: python manage.py db stamp head
worker: celery -A util.tasks worker
