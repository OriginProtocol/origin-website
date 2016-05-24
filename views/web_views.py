import apilib
from flask import json
from flask import render_template

from app import app

@app.route('/')
def index():
    return render_template('index.html')

class ClientConfig(object):
    def __init__(self, **kwargs):
        self.values = kwargs

    def __getattr__(self, name):
        return self.values[name]

    def to_json(self):
        d = {key: ClientConfig._to_raw_object(value) for key, value in self.values.iteritems()}
        return json.htmlsafe_dumps(d)

    @classmethod
    def _to_raw_object(cls, value):
        if value is None:
            return None
        if isinstance(value, apilib.Model):
            return value.to_json()
        elif isinstance(value, list) or isinstance(value, tuple):
            return [cls._to_raw_object(item) for item in value]
        elif isinstance(value, dict):
            return {k: cls._to_raw_object(v) for k, v in value.iteritems()}
        return value
