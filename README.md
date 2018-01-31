# originprotocol.com

Official website for Origin Protocol

This is a pretty simple bare bones Flask app with the source code for [originprotocol.com](https://www.originprotocol.com). The code is all `Python 2.7` and we use `Postgres` for the database (basically just for the mailing list). The database is not required to be configured if you're just working on the website.

## Installing
_Note: This site is set up differently from typical virtualenv/flask applications._

Setup a virtualenv
```
virtualenv company-website && cd company-website
```

Clone
```
git clone https://github.com/OriginProtocol/company-website.git && cd company-website
```

Enter virtual environment
```
source env.sh
```

Install requirements
```
pip install -r requirements.txt
```

### Optional but Recommended
Installing redis is required to run background jobs via Celery.
Right now, Celery is only being used to send emails. In the near
future, however, we will be relying on Celery for additional
functionality. In the spirit of keeping things backwards compatible,
redis is not required as of this version, but it will be soon.

Install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)

Install redis locally.

On OSX you can use `brew` to install redis:
```
brew install redis
```

### Setting up the environment
Create a file named `.env`  in this directory that looks something like this:

    DEV_EMAIL = "foo@bar.com"
    DEBUG = True

    HOST = localhost
    HTTPS = False

    # Optional but recommended. If you use redis for other projects locally,
    # make sure to use a unique database number if 8 is already being used.
    # If you are not using redis, do not define this variable.
    REDIS_URL = redis://127.0.0.1:6379/8

    PROJECTPATH = "/"

    FLASK_SECRET_KEY = putyoursupersecretkeyhere

    DATABASE_URL = postgresql://localhost/origin

    SENDGRID_API_KEY = putyoursupersecretkeyhere

    TEMPLATE_ROOT = os.path.join(PROJECTPATH, 'templates')
    STATIC_ROOT = os.path.join(PROJECTPATH, 'static')

## Run it!

Without redis:
```
python main.py
```

With redis:
```
heroku local
```

Open browser to view
```
open http://127.0.0.1:5000/
```

**Problems?** Hit us up in the `eng-website` channel on [Slack](https://slack.originprotocol.com) if you need help.

## Localization
See README in `translations` directory
