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

Create a file named `.env`  in this directory that looks something like this:

    DEV_EMAIL = "foo@bar.com"
    DEBUG = True

    HOST = localhost
    HTTPS = False

    PROJECTPATH = "/"

    FLASK_SECRET_KEY = putyoursupersecretkeyhere

    DATABASE_URL = postgresql://localhost/origin

    SENDGRID_API_KEY = putyoursupersecretkeyhere

    TEMPLATE_ROOT = os.path.join(PROJECTPATH, 'templates')
    STATIC_ROOT = os.path.join(PROJECTPATH, 'static')

Run it!
```
python main.py
```

Open browser to view
```
open http://127.0.0.1:5000/
```

**Problems?** Hit us up in the `eng-website` channel on [Slack](https://slack.originprotocol.com) if you need help.

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
