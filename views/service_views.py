import apilib
from flask import json
from flask import request

from app import app


def serviceroute(service_class):
    return app.route(
        service_class.path +
        '/' +
        '<method_name>',
        methods=['POST'])


def invoke_service(service_class, method_name, **kwargs):
    request_json = request.json
    service = service_class(**kwargs)
    response = service.invoke_with_json(method_name, request_json)
    response_code = 200
    if response['response_code'] == apilib.ResponseCode.SERVER_ERROR:
        response_code = 500
    elif response['response_code'] == apilib.ResponseCode.REQUEST_ERROR:
        response_code = 400
    return json.jsonify(response), response_code
