# originprotocol.com

This is a pretty simple bare bones Flask app with the source code for [originprotocol.com](https://www.originprotocol.com). The code is all `Python 2.7` and we use `Postgres` for the database (basically just for the mailing list).

To get started (we recommend doing this in an virtualenv):

    git clone https://github.com/OriginProtocol/company-website.git
    pip install -r requirements.txt

We should also mention that the app expects a `.env` file in your root directory that looks something like this:

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

Hit us up in the `eng-website` channel on [Slack](http://slack.originprotocol.com) if you need help.

## Localization

Use this command to extract strings into a file `messages.pot`
```
pybabel extract -F babel.cfg -o messages.pot --input-dirs=. --no-wrap
```

After translations are updated, yse this to compile them
```
pybabel update -i messages.pot -d translations
```
