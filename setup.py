#! /usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='origin-website',
    install_requires=[
        'alembic~=1.5.8',
        'Babel~=2.9.0',
        'backoff~=1.10.0',
        'beautifulsoup4>=4.9.3',
        'celery~=5.0.5',
        'factory-boy>=3.2.0',
        'Flask~=1.1.2',
        'Flask-Babel~=2.0.0',
        'Flask-Compress~=1.9.0',
        'Flask-Migrate~=2.7.0',
        'Flask-Script~=2.0.6',
        'Flask-SQLAlchemy~=2.5.1',
        'flask_cors~=3.0.10',
        'FullContact.py>=0.0.6',
        'geoip2~=4.1.0',
        'google-api-python-client>=1.12',
        'google-auth-oauthlib>=0.4.4',
        'Jinja2~=2.11.3',
        'nameparser~=1.0.6',
        'psycopg2~=2.8.6',
        'pyOpenSSL>=20.0.1',
        'python-dateutil~=2.8.1',
        'python_dotenv>=0.16.0',
        'pyuca>=1.2',
        'pyyaml>=5.4.1',
        'ratelimit~=2.2.1',
        'raven[flask]~=6.10.0',
        'redis~=3.5.3',
        'requests~=2.25.1',
        'sendgrid~=6.6.0',
        'SQLAlchemy~=1.4.3',
        'timeago~=1.0.15',
        # The following are pinned to clear up some issues but they're only
        # grandchildren dependencies
        'click<8',
        'google-auth<2'
    ],
    extras_require={
        'dev': [
            'Faker>=7.0.1',
            'mock>=4.0.3',
            'pytest>=6.2.2',
            'pytest-env>=0.6.2',
            'testing.postgresql>=1.3.0',
            'testing.common.database>=2.0.3',
        ],
        'deploy': ['gunicorn>=20.1.0', 'newrelic>=6.2.0.156']
    },
    packages=find_packages(),
    package_data={
        'data': ['ip2geo/GeoLite2-Country.mmdb'],
    }
)
