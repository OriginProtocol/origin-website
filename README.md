![origin_github_banner](https://user-images.githubusercontent.com/673455/37314301-f8db9a90-2618-11e8-8fee-b44f38febf38.png)

![origin_license](https://img.shields.io/badge/license-MIT-6e3bea.svg?style=flat-square&colorA=111d28)

# originprotocol.com

Official website for Origin Protocol

This is a Flask app with the source code for [www.originprotocol.com](https://www.originprotocol.com). The code is all `Python 2.7` with `Postgres` for the database (basically just for the mailing list). The database is not required to be configured if you're just working on the website.

## Installing

Setup a virtualenv
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

Rename the file `sample.env` to `.env`, and update env variables as desired.
```
mv sample.env .env
```

Run it!
```
python main.py
```

Open browser to view
```
open http://127.0.0.1:5000/
```

**Problems?** Hit us up in the `engineering` channel on [Discord](https://www.originprotocol.com/discord) if you need help.

## Run the Tests


Throughout the development process and before committing or deploying, run:

```bash
pytest
```

Run individual test files simply as:

```bash
pytest path/to/test.py
```

Run a single test case, or an individual test, using:

```bash
pytest path/to/test.py::test_case_name
```
## Running locally with Celery

We use [celery](http://flask.pocoo.org/docs/0.12/patterns/celery/) for running background tasks (mostly just sending emails). To get this working on your local machine, you'll want to make sure:

 - Your .env has `CELERY_DEBUG: False`
 - Redis is installed and running: `redis-server`
 - An active celery worker is running: `celery -A util.tasks worker`

## Localization
See [translations](translations) directory. 

## Database changes

We use [Flask Migrate](https://flask-migrate.readthedocs.io/en/latest/) to handle database revisions. If you make changes to the database, use `flask db migrate` to generate the required migration file and then `flask db upgrade` to implement and test your changes on your local database before committing.

## Heroku Deploy

To deploy a development copy of the site on Heroku, just choose which branch you would like to use and follow the instructions: 

| `Master` branch <br>(stable) | `Develop` branch<br> (active development) | 
|---------|----------|
| [![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/originprotocol/company-website/tree/master) | [![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/originprotocol/company-website/tree/develop) | 

Heroku will prompt you to set config variables. At a minium, you must set these two:

|Config          |Value|
|----------------|------|
|FLASK_SECRET_KEY|(make something up)|
|HOST            |(domain name of your dev heroku app)|

See [sample.env](sample.env) for a full list of other optional config variables. You can [get Recaptcha keys from Google](https://www.google.com/recaptcha/admin).

We use both the python and the nginx buildpacks:

	heroku buildpacks:set heroku/python
	heroku buildpacks:add https://github.com/heroku/heroku-buildpack-nginx

## Contributing

We'd love to have you join us and contribute to this project. Please join our [#engineering channel on Discord](http://www.originprotocol.com/discord) and read our [guidelines on contributing](http://docs.originprotocol.com/#contributing) to get started.


