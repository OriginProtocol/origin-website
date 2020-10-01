![origin_github_banner](https://user-images.githubusercontent.com/673455/37314301-f8db9a90-2618-11e8-8fee-b44f38febf38.png)

![origin_license](https://img.shields.io/badge/license-MIT-6e3bea.svg?style=flat-square&colorA=111d28)

Head to https://www.originprotocol.com/developers to learn more about what we're building and how to get involved.

# originprotocolofficial.com

Official website for Origin Protocol

This is a Flask app with the source code for [www.originprotocol.com](https://www.originprotocol.com). The code is all `Python 2.7` with `Postgres` for the database (basically just for the mailing list). The database is not required to be configured if you're just working on the website.

## Installing

Setup a virtualenv
```
virtualenv --python=/usr/local/bin/python2 origin-website && cd origin-website
```

Clone
```
git clone https://github.com/OriginProtocol/origin-website.git && cd origin-website
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

We use [Celery](http://flask.pocoo.org/docs/0.12/patterns/celery/) for running background tasks (mostly just sending emails). To get this working on your local machine, you'll want to make sure:

 - Your .env has `CELERY_DEBUG: False`
 - Redis is installed and running: `redis-server`
 - An active Celery worker is running: `celery --loglevel=INFO -A util.tasks worker`

 [Celery Flower](http://flower.readthedocs.io/en/latest/install.html#usage) is useful for monitoring tasks: `flower -A util.tasks --port=5555`

## Running locally with Docker Compose

You can run the website in combination with a local PostgreSQL, Redis and Celery using [Docker Compose](https://docs.docker.com/compose/).
```bash
cd origin-website
docker-compose up
```

Note: you can login to the container running the app with the following command:
```bash
docker exec -ti origin-website /bin/bash
```

## Running cron jobs locally
Some scripts use Heroku cron jobs. Use the following command to test them locally
```bash
PYTHONPATH=$(pwd) PROJECTPATH=$(pwd) python ./logic/scripts/update_token_insight.py
```

When running on docker:
```bash
docker exec -it -e PYTHONPATH=/app -e PROJECTPATH=/app origin-website python ./logic/scripts/update_token_insight.py
```

## Running cron jobs on Production/Staging
Running token_stats on Staging:
```bash
heroku run -a staging-originprotocol-com PROJECTPATH=/app python ./logic/scripts/token_stats.py
```

Running token_stats on Production:
```bash
heroku run -a originprotocol-com PROJECTPATH=/app python ./logic/scripts/token_stats.py
```


### System Requirements

- [Docker](https://docs.docker.com/install/overview/) **version 18 or greater**:
`docker --version`
- [Docker Compose](https://docs.docker.com/compose/) **For Mac and Windows docker-compose should be part of desktop Docker installs**:
`docker-compose --version`
- [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git):
`git --version`
- Unix-based system (OSX or Linux) needed to run the bash scripts

### Getting Started

1. Clone the repository

`git clone https://github.com/OriginProtocol/origin-website && cd origin-website`

2. From the root of the repository run `docker-compose up`. The first time this command runs it will take some time to complete due to the initial building of the containers.

When this completes you should be able to access the website at `http://localhost:5000`.

## Localization
See [translations](translations) directory.

## Database changes

We use [Flask Migrate](https://flask-migrate.readthedocs.io/en/latest/) to handle database revisions. If you make changes to the database, use `flask db migrate` to generate the required migration file and then `flask db upgrade` to implement and test your changes on your local database before committing.

## Heroku Deploy

To deploy a development copy of the site on Heroku, just choose which branch you would like to use and follow the instructions:

| `stable` branch <br>(v1.11.1) | `master` branch<br> (active development) |
|---------|----------|
| [![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/originprotocol/origin-website/tree/stable) | [![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/originprotocol/origin-website/tree/master) |

Heroku will prompt you to set config variables. At a minium, you must set these two:

|Config          |Value|
|----------------|------|
|FLASK_SECRET_KEY|(make something up)|
|HOST            |(domain name of your dev heroku app)|

See [sample.env](sample.env) for a full list of other optional config variables. You can [get Recaptcha keys from Google](https://www.google.com/recaptcha/admin).

We use both the python and the nginx buildpacks:

	heroku buildpacks:set heroku/python
	heroku buildpacks:add https://github.com/heroku/heroku-buildpack-nginx

## Connect to Heroku instance

In order to run Celery jobs manually you can ssh into Heroku staging with: 
`heroku ps:exec --app staging-originprotocol-com` 

or into Heroku production
`heroku ps:exec --app originprotocol-com` 

## Contributing

We'd love to have you join us and contribute to this project. Please join our [#engineering channel on Discord](http://www.originprotocol.com/discord) and read our [guidelines on contributing](http://docs.originprotocol.com/#contributing) to get started.

## Shoutouts

Special thanks to the following companies for their support:

<a href="https://infura.io"><img src="https://www.originprotocol.com/static/img/infura.png" height="40"></a> 
<a href="https://protocol.ai/"><img src="https://www.originprotocol.com/static/img/protocol-labs.png" height="40"></a>
<a href="https://www.browserstack.com"><img src="https://www.originprotocol.com/static/img/browserstack.svg" height="40"></a>
