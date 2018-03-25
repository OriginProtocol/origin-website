# originprotocol.com

Official website for Origin Protocol

This is a Flask app with the source code for [www.originprotocol.com](https://www.originprotocol.com). The code is all `Python 2.7` with `Postgres` for the database (basically just for the mailing list). The database is not required to be configured if you're just working on the website.

## Installing
_Note: This site is set up differently from typical virtualenv/flask applications._

Setup a virtualenv
```
virtualenv company-website && cd company-website
```

Note: As of Feb 2018, Homebrew on MacOS defaults to Python 3. Therefore you'll need to specify Python 2.7
```
virtualenv --python=/usr/local/bin/python2 company-website && cd company-website
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

<<<<<<< HEAD
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
=======
Rename the file `sample.env` to `.env`, and update env variables as desired.
```
mv sample.env .env
```
>>>>>>> 1acf4322168a9b679b68d40434aededa5a37cdfb

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

**Problems?** Hit us up in the `engineering` channel on [Discord](https://www.originprotocol.com/discord) if you need help.

## Localization
See README in `translations` directory

## Database changes

We use [Flask Migrate](https://flask-migrate.readthedocs.io/en/latest/) to handle database revisions. If you make changes to the database, use `flask db migrate` to generate the required migration file and then `flask db upgrade` to implement and test your changes on your local database before committing.

## Recaptcha

To enable recaptcha, add the following environment variables to `.env`

    RECAPTCHA_SITE_KEY = "<YOUR SITE KEY>"
    RECAPTCHA_SECRET_KEY = "<YOUR SECRET KEY>"
    RECAPTCHA_SIZE = "invisible"

You can get Recaptcha keys here: https://www.google.com/recaptcha/admin

## Dev Deployment on Heroku

To deploy a dev copy of the site on Heroku, you'll follow the normal steps you would to deploy on Heroku, with two additional steps.

After the normal setup and linking, you'll need to ensure the site uses both the python and the nginx backend:

	heroku buildpacks:set heroku/python
	heroku buildpacks:add https://github.com/heroku/heroku-buildpack-nginx

As a minium, you must set these three Heroku config variables:

|Config          |Value|
|----------------|------|
|FLASK_SECRET_KEY|(make something up)|
|PROJECTPATH     |/app|
|HOST            |(domain name of your dev heroku app)|

There are more optional config variables you can set. See [sample.env](sample.env) for a full list.


