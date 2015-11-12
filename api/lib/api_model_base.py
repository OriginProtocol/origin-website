# Based on https://github.com/tals/uber.py/blob/master/uber/model_base.py

from StringIO import StringIO
from datetime import datetime
import decimal
import inspect
import json
import os
from pprint import pformat
from dateutil.parser import DEFAULTPARSER as dateparser

from api.lib import api_validators

class Model(object):
    def __init__(self, data=None):
        self._data = data or {}

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, pformat(self._data))

    def __str__(self):
        return ModelPrinter().pprint(self)

    def __eq__(self, other):
        return type(self) == type(other) and self._data == other._data

    @property
    def raw(self):
        return self._data

    def raw_json_str(self):
        return json.dumps(self.raw)

    @classmethod
    def new(cls, **kwargs):
        data = {}
        for key, value in kwargs.iteritems():
            field = cls.field_for_field_name(key)
            if isinstance(field, ModelField):
                raw_value = value.raw if value else None
            elif isinstance(field, ListField):
                if value and inspect.isclass(field._item_type) and issubclass(field._item_type, Model):
                    raw_value = [v.raw if v is not None else None for v in value]
                else:
                    raw_value = value
            elif isinstance(field, DictField) and value:
                raw_value = {k: v.raw if isinstance(v, Model) else v for k, v in value.iteritems()}
            else:
                raw_value = value
            data[key] = raw_value
        return cls(data)

    def update(self, other):
        self._data.update(other.raw)

    def update_fields(self, **kwargs):
        self._data.update(kwargs)

    def attr_name_for_field(self, field):
        self._build_field_mappings()
        return self._field_to_attr_name[field]

    def get_value_for_field(self, field):
        attr_name = self.attr_name_for_field(field)
        return getattr(self, attr_name)

    @classmethod
    def model_name(cls):
        return cls.__name__

    @classmethod
    def all_fields(cls):
        cls._build_field_mappings()
        return cls._field_to_attr_name.keys()

    @classmethod
    def field_for_field_name(cls, field_name):
        cls._build_field_mappings()
        return cls._field_name_to_field.get(field_name)

    @classmethod
    def field_items(cls):
        cls._build_field_mappings()
        return [(v, k) for k, v in cls._field_to_attr_name.iteritems()]

    @classmethod
    def _build_field_mappings(cls):
        if not hasattr(cls, '_field_to_attr_name'):
            cls._field_to_attr_name = {}
            cls._field_name_to_field = {}
            for attr_name in dir(cls):
                field = getattr(cls, attr_name, None)
                if field and isinstance(field, Field):
                    cls._field_to_attr_name[field] = attr_name
                    cls._field_name_to_field[field._name] = field

class Field(object):
    base_validators = ()
    type_name = 'Any type'

    """
    Basic json field. Returns as is.
    """
    def __init__(self, name, validators=(), required=False, readonly=False):
        """
        Args:
             - name: the key of the json field
             - required: either a boolean or a tuple of method names for which this field is required
             - readonly: either a boolean or a tuple of method names for which this field is readonly
        """
        self._name = name
        self.required = required
        self.readonly = readonly
        implicit_validators = []
        if required:
            methods = required if type(required) != bool else None
            implicit_validators.append(api_validators.Required(methods))
        if readonly:
            methods = readonly if type(readonly) != bool else None
            implicit_validators.append(api_validators.Readonly(methods))            
        self._validators = implicit_validators + list(self.base_validators) + list(validators)

    def __get__(self, instance, owner):
        if instance:
            value = instance._data.get(self._name)
            return self.to_python(value)
        else:
            return self

    def __set__(self, instance, value):
        instance._data[self._name] = self.from_python(value)

    def to_python(self, value):
        return value

    def from_python(self, python_value):
        return python_value

    # Only for documentation

    def get_type_name(self):
        return self.type_name

    def get_parameter_type_name(self):
        return None

    def parameter_is_model(self):
        return False

class ModelField(Field):
    """
    Translates a field to the given Model type
    """
    def __init__(self, name, model_type, **kwargs):
        super(ModelField, self).__init__(name, **kwargs)
        self._model_type = model_type

    def to_python(self, value):
        if value is None:
            return None

        return self._model_type(value)

    def from_python(self, python_value):
        return python_value.raw if python_value else None

    def get_type_name(self):
        return self._model_type.model_name()

class ListField(Field):
    """
    Translates a field to a list, where the individual values are the result of calling value_func
    If the list does not exists and the field is optional, returns []
    """
    def __init__(self, name, item_func, **kwargs):
        super(ListField, self).__init__(name, **kwargs)
        self._item_type = item_func

    def to_python(self, value):
        if value is None:
            return []

        return [self._item_type(x) if x is not None else None for x in value]

    def from_python(self, python_value):
        if python_value is None:
            return None
        if issubclass(self._item_type, Model):
            return [item.raw for item in python_value]
        return python_value

    def get_type_name(self):
        return 'List'

    def get_parameter_type_name(self):
        if self.parameter_is_model():
            return self._item_type.model_name()
        return _get_type_name_from_primitive(self._item_type)

    def parameter_is_model(self):
        return inspect.isclass(self._item_type) and issubclass(self._item_type, Model)

class DictField(Field):
    """
    Translates a field to a dict, where the individual values are the result of calling value
    If the list does not exists and the field is optional, returns {}
    """
    def __init__(self, name, value, key=None, **kwargs):
        """
        Args:
            - name: the field name
            - value: a type (or a callable) of the value
            - key: a type (or a callable) of the keys
        """
        super(DictField, self).__init__(name, **kwargs)
        self._item_type = value
        self._key_func = key or (lambda x: x)

    def to_python(self, value):
        if value is None:
            return {}

        return {self._key_func(k): self._item_type(v) for k, v in value.items()}

    def get_type_name(self):
        return 'Dict'

    def get_parameter_type_name(self):
        if self.parameter_is_model():
            return self._item_type.model_name()
        return _get_type_name_from_primitive(self._item_type)

    def parameter_is_model(self):
        return inspect.isclass(self._item_type) and issubclass(self._item_type, Model)

class DateTimeField(Field):
    type_name = 'DateTime'

    """
    Parses a datetime string to a string
    """
    def to_python(self, value):
        if value is None:
            return None
        return dateparser.parse(value)

    def from_python(self, python_value):
        if python_value is None:
            return None
        return unicode(python_value.isoformat())

class EpochField(Field):
    type_name = 'Epoch'

    def to_python(self, value):
        return datetime.utcfromtimestamp(value/1000.0)

class BooleanField(Field):
    type_name = 'Boolean'

    base_validators = (api_validators.BooleanType(),)

class FloatField(Field):
    type_name = 'Float'

    base_validators = (api_validators.FloatType(),)

class IntegerField(Field):
    type_name = 'Integer'

    base_validators = (api_validators.IntegerType(),)

class StringField(Field):
    type_name = 'String'

    base_validators = (api_validators.StringType(),)

class CurrencyField(Field):
    type_name = 'Currency'

    base_validators = (api_validators.DecimalIntegerType(),)

    def to_python(self, value):
        if value is None:
            return None
        return decimal.Decimal(value)

    def from_python(self, python_value):
        if python_value is None:
            return None
        return int(python_value)

# TODO: Add validation
class EnumField(StringField):
    type_name = 'Enum'

class ModelPrinter(object):
    """
    a pretty-printer. Inspired by pprint.py
    getting good results out of pprint was way too hacky, mainly due to the different naming convention of the fields in
    __repr__ vs __str__
    """
    def __init__(self):
        self._stream = StringIO()
        self._padding = '    '

    def pprint(self, obj):
        self._pprint_model(obj, 0)
        self._stream.seek(0)
        return self._stream.getvalue()

    def _write(self, data):
        self._stream.write(data)

    def _write_padding(self, data='', depth=0):
        data = self._padding * depth + data
        self._stream.write(data)

    def _pprint_obj(self, obj, depth):
        if isinstance(obj, Model):
            self._pprint_model(obj, depth)
        elif isinstance(obj, list):
            self._write('[\n')
            self._pprint_array(obj, depth + 1)
            self._write_padding(']', depth)
        elif isinstance(obj, dict):
            self._write('{\n')
            self._pprint_dict(obj, depth + 1)
            self._write_padding('}', depth)
        elif isinstance(obj, datetime):
            self._write(str(obj))
        else:
            self._write(pformat(obj, indent=1, depth=depth))

    def _pprint_model(self, obj, depth):
        self._write('<class %s>'% type(obj).__name__)
        self._write('\n')
        depth += 1
        for name, field in sorted(type(obj).field_items(), key=lambda pair: pair[0]):
            value = obj.get_value_for_field(field)
            if value is None:
                continue

            self._write_padding(name + ': ', depth)
            self._pprint_obj(value, depth)

            self._write('\n')

        self._stream.seek(-1, os.SEEK_CUR)

    def _pprint_dict(self, dict_field, depth):
        for k, v in dict_field.items():
            self._write_padding(depth=depth, data='{}:  '.format(k))
            self._pprint_obj(depth=depth, obj=v)
            self._write('\n')

    def _pprint_array(self, array, depth):
        for item in array:
            self._write_padding(depth=depth)
            self._pprint_obj(depth=depth, obj=item)
            self._write(',\n')

def _get_type_name_from_primitive(primitive_type):
    if primitive_type in (int, long):
        return 'Integer'
    elif inspect.isclass(primitive_type):
        if issubclass(primitive_type, basestring):
            return 'String'
        elif issubclass(primitive_type, dict):
            return 'Dict'
    return ''
