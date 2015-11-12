import inspect

from api.lib import api_model_base

def validate(model, error_context, context=None):
    for name, field in model.__class__.__dict__.iteritems():
        if not isinstance(field, api_model_base.Field):
            continue

        value = getattr(model, name, None)
        child_error_context = error_context.extend_path_for_field(field._name)
        if context:
            context = context.for_model(model)
        for validator in field._validators:
            value = validator.validate(value, child_error_context, context)
        setattr(model, name, value)

        if isinstance(field, api_model_base.ModelField):
            if value:
                validate(value, child_error_context, context)
        elif isinstance(field, api_model_base.ListField):
            if value and issubclass(field._item_type, api_model_base.Model):
                for i, item in enumerate(value):
                    if item:
                        item_error_context = child_error_context.extend_path_for_index(i)
                        item = validate(item, item_error_context, context)
                        value[i] = item
        elif isinstance(field, api_model_base.DictField):
            if value and inspect.isclass(field._item_type) and issubclass(field._item_type, api_model_base.Model):
                for key, item in value.iteritems():
                    if item:
                        item_error_context = child_error_context.extend_path_for_dict_key(key)
                        item = validate(item, item_error_context, context)
                        value[key] = item
