web: newrelic-admin run-program gunicorn main:app
init: python manage.py db init
migrate: python manage.py db migrate
upgrade: python manage.py db upgrade
worker: celery -A util.tasks worker
