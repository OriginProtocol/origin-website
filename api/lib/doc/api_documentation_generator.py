import operator

from api.lib import api_model_base
from api.lib import api_service_base
from api.lib import api_validators

class FieldInfo(object):
    def __init__(self, name=None, type_name=None, is_model=None,
        parameter_type_name=None, parameter_is_model=None, constraints=None):
        self.name = name
        self.type_name = type_name
        self.is_model = is_model
        self.parameter_type_name = parameter_type_name
        self.parameter_is_model = parameter_is_model
        self.constraints = constraints or ()

    @classmethod
    def from_field(cls, field):
        return FieldInfo(
            name=field._name,
            type_name=field.get_type_name(),
            is_model=isinstance(field, api_model_base.ModelField),
            parameter_type_name=field.get_parameter_type_name(),
            parameter_is_model=field.parameter_is_model(),
            constraints=[val.get_documentation() for val in field._validators if  not isinstance(val, api_validators.TypeValidator)])

class ModelInfo(object):
    def __init__(self, name=None, fields=None):
        self.name = name
        self.fields = fields or ()

    @classmethod
    def from_model(cls, model_class):
        field_infos = [FieldInfo.from_field(field) for field in model_class.all_fields()]
        return ModelInfo(model_class.model_name(),
            sorted(field_infos, key=operator.attrgetter('name')))

class MethodInfo(object):
    def __init__(self, name=None, url=None, request=None, response=None):
        self.name = name
        self.url = url
        self.request = request
        self.response = response

class ServiceInfo(object):
    def __init__(self, name=None, methods=None):
        self.name = name
        self.methods = methods or ()

    @classmethod
    def from_service(cls, service_class):
        methods = []
        for method_descriptor in service_class.METHODS.itervalues():
            methods.append(MethodInfo(
                method_descriptor.method_name,
                service_class.BASE_PATH + method_descriptor.method_name,
                ModelInfo.from_model(method_descriptor.request_class),
                ModelInfo.from_model(method_descriptor.response_class)))
        return ServiceInfo(service_class.__name__, methods)        

# Import all modules that contain models first, then call this to look
# for model subclasses.
def get_all_models():
    models = api_model_base.Model.__subclasses__()
    models.remove(api_service_base.ApiServiceRequest)
    models.remove(api_service_base.ApiServiceResponse)
    return models

# Import all modules that contain services first, then call this to look
# for service subclasses.
def get_all_services():
    services = api_service_base.ApiService.__subclasses__()
    services.remove(api_service_base.ApiRemoteServiceStub)
    services.remove(api_service_base.ApiServiceImplementation)
    return services


class DocumentationGenerator(object):
    def __init__(self, title=None, model_classes=None, service_classes=None):
        self.title = title
        self.model_classes = model_classes or ()
        self.service_classes = service_classes or ()

    def generate(self):
        raise NotImplementedError()

class TextDocumentationGenerator(DocumentationGenerator):
    def generate(self):
        for model_class in sorted(self.model_classes, key=lambda m: m.model_name()):
            self.generate_for_model(model_class)
            print
        for service_class in sorted(self.service_classes, key=lambda s: s.__name__):
            self.generate_for_service(service_class)
            print

    def generate_for_model(self, model_class):
        model_info = ModelInfo.from_model(model_class)

        print '%s:' % model_info.name
        for field_info in model_info.fields:
            if field_info.parameter_type_name:
                print '  %s (%s<%s>)' % (field_info.name, field_info.type_name, field_info.parameter_type_name)
            else:
                print '  %s (%s)' % (field_info.name, field_info.type_name)
            for constraint in field_info.constraints:
                print '    %s' % constraint

    def generate_for_service(self, service_class):
        service_info = ServiceInfo.from_service(service_class)

        print 'Service %s:' % service_info.name
        for method_info in service_info.methods:
            print '  %s(%s) returns %s - %s' % (
                method_info.name,
                method_info.request.name,
                method_info.response.name,
                method_info.url)

# Requires the jinja2 template library to be installed
class JinjaHtmlDocumentationGenerator(DocumentationGenerator):
    def generate(self):
        model_infos = [ModelInfo.from_model(model_class) for model_class in self.model_classes]
        service_infos = [ServiceInfo.from_service(service_class) for service_class in self.service_classes]
        jinja_env = self.setup_env()
        return jinja_env.get_template('api_documentation.html').render(
            title=self.title,
            models=sorted(model_infos, key=operator.attrgetter('name')),
            services=sorted(service_infos, key=operator.attrgetter('name')))

    def setup_env(self):
        import os
        import jinja2
        import constants

        return jinja2.Environment(loader=jinja2.FileSystemLoader(
            os.path.join(constants.PROJECTPATH, 'api/lib/doc')))
