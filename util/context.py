import werkzeug
from flask import url_for


def create_contexts(app):
    @app.context_processor
    def campaign_context():
        """ template context processors """
        def url(req, **kwargs):
            """ Add a function url() to make building URLs for views easier """
            if req.url_rule and req.url_rule.endpoint:
                endpoint = req.url_rule.endpoint
            elif req.path != '/':
                endpoint = req.path
            else:
                endpoint = 'index'

            view_args = {}
            if view_args:
                view_args.update(req.view_args)
            view_args.update(kwargs)

            try:
                return url_for(endpoint, **view_args)
            except werkzeug.routing.BuildError:
                return url_for('index', **view_args)
        return {'url': url}
