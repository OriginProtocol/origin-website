import traceback

import json
import requests

from api.lib import api_model_base
from api.lib import api_model_validation
from api.lib import api_validators
from app import app

class ApiServiceError(api_model_base.Model):
    error_code = api_model_base.StringField('error_code')
    message = api_model_base.StringField('message')
    field_path = api_model_base.StringField('field_path')

    def __str__(self):
        return '%s: error_code: %s, message: %s, field_path: %s' % (
            type(self).__name__, self.error_code, self.message, self.field_path)

class ApiServiceRequest(api_model_base.Model):
    validate_only = api_model_base.BooleanField('validate_only')

class ApiServiceResponse(api_model_base.Model):
    response_code = api_model_base.StringField('response_code')
    errors = api_model_base.ListField('errors', ApiServiceError)

class ApiResponseCode(object):
    SUCCESS = 'SUCCESS'
    SERVER_ERROR = 'SERVER_ERROR'
    REQUEST_ERROR = 'REQUEST_ERROR'


class ApiServiceException(Exception):
    def __init__(self, response_code=None, errors=()):
        self.response_code = response_code
        self.errors = errors

    def __str__(self):
        return '%s, errors: %s' % (self.response_code,
            ', '.join(str(e) for e in self.errors))

    @classmethod
    def server_error(cls, errors=(), error_msgs=()):
        api_errors = list(errors) + [ApiServiceError.new(message=msg) for msg in error_msgs]
        return ApiServiceException(ApiResponseCode.SERVER_ERROR, api_errors)

    @classmethod
    def request_error(cls, errors=(), error_msgs=()):
        api_errors = list(errors) + [ApiServiceError.new(message=msg) for msg in error_msgs]
        return ApiServiceException(ApiResponseCode.REQUEST_ERROR, api_errors)


class MethodDescriptor(object):
    def __init__(self, method_name, request_class, response_class):
        self.method_name = method_name
        self.request_class = request_class
        self.response_class = response_class

def servicemethods(*methods):
    result = {} 
    for method_name, request_class, response_class in methods:
        result[method_name] = MethodDescriptor(method_name, request_class, response_class)
    return result

class ApiService(object):
    METHODS = servicemethods()
    BASE_PATH = None

class ApiServiceImplementation(ApiService):
    def invoke(self, method_name, request):
        method_descriptor = self.resolve_method(method_name)
        method = getattr(self, method_descriptor.method_name)
        try:
            self.validate(request, method_name)
            if request and request.validate_only:
                response = method_descriptor.response_class()
            else:
                response = method(request)
            response.response_code = ApiResponseCode.SUCCESS
        except ApiServiceException as e:
            response = method_descriptor.response_class()
            self.process_exception(e, response)
        except AssertionError:
            # Re-raise for assertions made in unittests
            raise
        except Exception as e:
            if app.config.get('RERAISE_API_EXCEPTIONS'):
                raise
            response = method_descriptor.response_class()
            response.response_code = ApiResponseCode.SERVER_ERROR

        if response.response_code == ApiResponseCode.SERVER_ERROR:
            app.logger.error('Server error in API call %s.%s\nRequest:\n%s\nResponse: %s\n%s',
                self.__class__.__name__,
                method_name,
                json.dumps(request.raw if request else None),
                json.dumps(response.raw if response else None),
                traceback.format_exc() or '')

        return response

    def invoke_with_json(self, method_name, json_request):
        method_descriptor = self.resolve_method(method_name)
        request = method_descriptor.request_class(json_request)
        response = self.invoke(method_name, request)
        return response.raw if response else None

    def resolve_method(self, method_name):
        descriptor = self.METHODS.get(method_name)
        if not descriptor:
            raise Exception('No descriptor for method of name %s' % method_name)
        if not hasattr(self, method_name):
            raise Exception('Method %s not implemented' % method_name)
        return descriptor

    def process_exception(self, exception, response):
        response.response_code = exception.response_code
        response.errors = exception.errors

    def validate(self, request, method_name):
        error_context = api_validators.ErrorContext()
        validation_context = api_validators.ValidationContext(method_name, self.__class__.__name__, request)
        api_model_validation.validate(request, error_context, validation_context)
        if error_context.has_errors():
            errors = [ApiServiceError.new(
                error_code=error.code,
                message=error.msg,
                field_path=error.path) for error in error_context.errors]
            raise ApiServiceException(ApiResponseCode.REQUEST_ERROR, errors)

class ApiRemoteServiceStub(ApiService):
    def __init__(self, base_url):
        self.base_url = base_url

    def invoke(self, method_descriptor, request):
        url = '%s%s%s' % (self.base_url, self.BASE_PATH, method_descriptor.method_name)
        response = requests.post(url, data=request.raw)
        return method_descriptor.response_class(response.json())

    def __getattr__(self, method_name):
        descriptor = self.METHODS.get(method_name)
        if not descriptor:
            raise Exception('No method named %s defined on this service' % method_name)
        return lambda request: self.invoke(descriptor, request)

