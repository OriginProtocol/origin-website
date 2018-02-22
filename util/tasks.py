import os
import sendgrid
from celery import Celery
from config import constants
from flask import Flask

def make_celery(app):
    celery = Celery(app.import_name, backend=os.environ['REDIS_URL'],
                    broker=os.environ['REDIS_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

<<<<<<< HEAD
=======
flask_app = Flask(__name__)

flask_app.config.update(
    broker_url=os.environ['REDIS_URL'],
    result_backend=os.environ['REDIS_URL'],
    task_always_eager=os.environ.get('CELERY_DEBUG', False)
)

celery = make_celery(flask_app)


@celery.task()
>>>>>>> 1acf4322168a9b679b68d40434aededa5a37cdfb
def send_email(body):
    sg_api = sendgrid.SendGridAPIClient(apikey=constants.SENDGRID_API_KEY)
    sg_api.client.mail.send.post(request_body=body) 

# Conditionally bring Celery into the mix if there is a REDIS_URL
if os.environ.get('REDIS_URL') is not None:
    flask_app = Flask(__name__)
    flask_app.config.update(
        CELERY_BROKER_URL=os.environ['REDIS_URL'],
        CELERY_RESULT_BACKEND=os.environ['REDIS_URL']
    )
    celery = make_celery(flask_app)

    send_email = celery.task(send_email)
