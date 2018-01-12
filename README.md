# originprotocol.com

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
Then open browser to view.    
    
**Problems?** Hit us up in the `eng-website` channel on [Slack](http://slack.originprotocol.com) if you need help.
