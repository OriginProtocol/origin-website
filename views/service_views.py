from flask import json
from flask import request

from api.lib import api_service_base
from app import app

def serviceroute(service_class):
    return app.route(service_class.BASE_PATH + '<method_name>', methods=['POST'])

def invoke_service(service_class, method_name, response_hook=None, **kwargs):
    if 'json' not in request.content_type:
        request_json = json.loads(request.form['request'])
    else:
        request_json = request.json
    service = service_class(**kwargs)
    response = service.invoke_with_json(method_name, request_json)
    response_code = 200
    if response['response_code'] == api_service_base.ApiResponseCode.SERVER_ERROR:
        response_code = 500
    elif response['response_code'] == api_service_base.ApiResponseCode.REQUEST_ERROR:
        response_code = 400
    if response_hook:
        return response_hook(response), response_code
    return json.jsonify(response), response_code
