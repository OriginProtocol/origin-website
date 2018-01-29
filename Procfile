+rm .git/hooks/pre-push
web: newrelic-admin run-program gunicorn main:app
worker: celery -A util.tasks worker
