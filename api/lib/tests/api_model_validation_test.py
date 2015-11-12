import unittest

from api.lib import api_model_base
from api.lib import api_model_validation
from api.lib import api_validators as vals

context = vals.ValidationContext

class BasicModel(api_model_base.Model):
    string_field = api_model_base.StringField('string_field')

class SampleChildModel(api_model_base.Model):
    child_string_field = api_model_base.StringField('child_string_field')
    child_int_field = api_model_base.IntegerField('child_int_field')
    child_required_float_field = api_model_base.FloatField('child_required_float_field', required=True)

class SampleParentModel(api_model_base.Model):
    string_field = api_model_base.StringField('string_field')
    int_field = api_model_base.IntegerField('int_field')
    float_field = api_model_base.FloatField('float_field')
    bool_field = api_model_base.BooleanField('bool_field')
    required_string_field = api_model_base.StringField('required_string_field', required=True)
    required_on_insert_int_field = api_model_base.IntegerField('required_on_insert_int_field', required=('insert',))
    model_field = api_model_base.ModelField('model_field', SampleChildModel)
    required_model_field = api_model_base.ModelField('required_model_field', SampleChildModel, required=True)

class ModelWithServiceSpecificRequiredField(api_model_base.Model):
    service_specifc_required_int_field = api_model_base.IntegerField('service_specifc_required_int_field',
        required=['SampleService.insert'])

class ModelWithReadOnlyFields(api_model_base.Model):
    always_readonly_string_field = api_model_base.StringField('always_readonly_string_field', readonly=True)
    readonly_on_update_int_field = api_model_base.StringField('readonly_on_update_int_field', readonly=('update',))

class ModelWithNonemptyListField(api_model_base.Model):
    nonempty_string_list_field = api_model_base.ListField('nonempty_string_list_field', str,
        validators=[vals.NonemptyElements()])

class ModelWithUnique(api_model_base.Model):
    field_with_unique_constraint = api_model_base.ListField('field_with_unique_constraint', str,
        validators=[vals.Unique()])

class ModelWithUniqueFields(api_model_base.Model):
    field_with_unique_child_field_constraint = api_model_base.ListField('field_with_unique_child_field_constraint',
        BasicModel, validators=[vals.UniqueFields('string_field')])

class ModelWithRangeConstraints(api_model_base.Model):
    min_only = api_model_base.IntegerField('min_only', validators=[vals.Range(5)])
    max_only = api_model_base.IntegerField('max_only', validators=[vals.Range(max_=10)])
    min_and_max = api_model_base.IntegerField('min_and_max', validators=[vals.Range(1, 3)])
    float_min_and_max = api_model_base.FloatField('float_min_and_max', validators=[vals.Range(1.5, 5.5)])

class ModelWithDependentFields(api_model_base.Model):
    field1 = api_model_base.StringField('field1', validators=[vals.ExactlyOneNonempty('field1', 'field2')])
    field2 = api_model_base.StringField('field2', validators=[vals.ExactlyOneNonempty('field1', 'field2')])

class ModelWithDisinctFields(api_model_base.Model):
    field1 = api_model_base.StringField('field1', validators=[vals.DifferentThan('field2')])
    field2 = api_model_base.StringField('field2', validators=[vals.DifferentThan('field1')])

class ApiModelValidationTest(unittest.TestCase):
    def assertHasError(self, error_context, code, path):
        for error in error_context.errors:
            if error.path == path and error.code == code:
                return
        self.fail('Expected error %s at path "%s"' % (code, path))

    def test_full_model_no_errors(self):
        model = SampleParentModel.new(
            string_field='abc',
            int_field=123,
            float_field=1.25,
            bool_field=True,
            required_string_field='def',
            required_on_insert_int_field=135,
            model_field=SampleChildModel.new(
                child_string_field='foo',
                child_int_field=999,
                child_required_float_field=3.14),
            required_model_field=SampleChildModel.new(
                child_string_field='bar',
                child_int_field=888,
                child_required_float_field=2.22))
        error_context = vals.ErrorContext()
        api_model_validation.validate(model, error_context)
        self.assertFalse(error_context.has_errors())

    def test_empty_model_required_errors(self):
        model = SampleParentModel.new()
        error_context = vals.ErrorContext()
        api_model_validation.validate(model, error_context)
        self.assertEqual(2, len(error_context.errors))
        self.assertHasError(error_context, vals.CommonErrorCodes.REQUIRED, 'required_string_field')
        self.assertHasError(error_context, vals.CommonErrorCodes.REQUIRED, 'required_model_field')

    def test_missing_required_field_on_child(self):
        model = SampleParentModel.new(
            required_string_field='abc',
            required_model_field=SampleChildModel.new())
        error_context = vals.ErrorContext()
        api_model_validation.validate(model, error_context)
        self.assertEqual(1, len(error_context.errors))
        self.assertHasError(error_context, vals.CommonErrorCodes.REQUIRED, 'required_model_field.child_required_float_field')

    def test_missing_required_field_on_specific_method(self):
        model = SampleParentModel.new(
            required_string_field='abc',
            required_model_field=SampleChildModel.new(child_required_float_field=1.0))
        error_context = vals.ErrorContext()
        api_model_validation.validate(model, error_context, context('insert'))
        self.assertEqual(1, len(error_context.errors))
        self.assertHasError(error_context, vals.CommonErrorCodes.REQUIRED, 'required_on_insert_int_field')

    def test_missing_required_field_on_service_specific_method(self):
        model = ModelWithServiceSpecificRequiredField.new()
        error_context = vals.ErrorContext()
        api_model_validation.validate(model, error_context, context('insert', 'SampleService'))
        self.assertEqual(1, len(error_context.errors))
        self.assertHasError(error_context, vals.CommonErrorCodes.REQUIRED, 'service_specifc_required_int_field')

        model = ModelWithServiceSpecificRequiredField.new()
        error_context = vals.ErrorContext()
        api_model_validation.validate(model, error_context, context('insert', 'SomeOtherService'))
        self.assertFalse(error_context.has_errors())

        model = ModelWithServiceSpecificRequiredField.new()
        error_context = vals.ErrorContext()
        api_model_validation.validate(model, error_context, context('insert'))
        self.assertFalse(error_context.has_errors())

        model = ModelWithServiceSpecificRequiredField.new()
        error_context = vals.ErrorContext()
        api_model_validation.validate(model, error_context, None)
        self.assertFalse(error_context.has_errors())

    def test_wrong_value_types(self):
        model = SampleParentModel.new(
            string_field=102,
            int_field=u'123',
            bool_field=135,
            float_field='123',
            required_string_field='abc',
            required_model_field=SampleChildModel.new(
                child_int_field='abc',
                child_string_field=123,
                child_required_float_field=1.0))
        error_context = vals.ErrorContext()
        api_model_validation.validate(model, error_context)
        self.assertEqual(6, len(error_context.errors))
        self.assertHasError(error_context, vals.CommonErrorCodes.INVALID_TYPE, 'string_field')
        self.assertHasError(error_context, vals.CommonErrorCodes.INVALID_TYPE, 'int_field')
        self.assertHasError(error_context, vals.CommonErrorCodes.INVALID_TYPE, 'float_field')
        self.assertHasError(error_context, vals.CommonErrorCodes.INVALID_TYPE, 'bool_field')
        self.assertHasError(error_context, vals.CommonErrorCodes.INVALID_TYPE, 'required_model_field.child_string_field')
        self.assertHasError(error_context, vals.CommonErrorCodes.INVALID_TYPE, 'required_model_field.child_int_field')

    def test_always_readonly_fields_are_stripped_but_not_method_specific_fields(self):
        model = ModelWithReadOnlyFields.new(
            always_readonly_string_field='abc',
            readonly_on_update_int_field='def')
        error_context = vals.ErrorContext()
        api_model_validation.validate(model, error_context)
        self.assertIsNone(model.always_readonly_string_field)
        self.assertEqual('def', model.readonly_on_update_int_field)

        api_model_validation.validate(model, error_context, context('not_update'))
        self.assertEqual('def', model.readonly_on_update_int_field)

    def test_method_specific_readonly_fields_stripped(self):
        model = ModelWithReadOnlyFields.new(
            always_readonly_string_field='abc',
            readonly_on_update_int_field='def')
        error_context = vals.ErrorContext()
        api_model_validation.validate(model, error_context, context('update'))
        self.assertIsNone(model.always_readonly_string_field)
        self.assertIsNone(model.readonly_on_update_int_field)

    def test_nonempty_list_elements(self):
        model = ModelWithNonemptyListField.new(nonempty_string_list_field=['abc'])
        error_context = vals.ErrorContext()
        api_model_validation.validate(model, error_context)
        self.assertFalse(error_context.has_errors())

        model = ModelWithNonemptyListField.new(nonempty_string_list_field=['', ''])
        error_context = vals.ErrorContext()
        api_model_validation.validate(model, error_context)
        self.assertTrue(error_context.has_errors())
        self.assertEqual(2, len(error_context.errors))
        self.assertHasError(error_context, vals.CommonErrorCodes.NONEMPTY_ITEM_REQUIRED, 'nonempty_string_list_field[0]')
        self.assertHasError(error_context, vals.CommonErrorCodes.NONEMPTY_ITEM_REQUIRED, 'nonempty_string_list_field[1]')

    def test_unique_constraint(self):
        model = ModelWithUnique.new(field_with_unique_constraint=['unique', 'not_unique', None, 'not_unique'])
        error_context = vals.ErrorContext()
        api_model_validation.validate(model, error_context)
        self.assertEqual(1, len(error_context.errors))
        self.assertHasError(error_context, vals.CommonErrorCodes.DUPLICATE_VALUE, 'field_with_unique_constraint[3]')

    def test_unique_field_constraint(self):
        model = ModelWithUniqueFields.new(field_with_unique_child_field_constraint=[
            BasicModel.new(string_field='unique'),
            BasicModel.new(string_field='not_unique'),
            BasicModel.new(string_field='also_unique'),
            BasicModel.new(),
            BasicModel.new(string_field='not_unique'),
            BasicModel.new()
            ])
        error_context = vals.ErrorContext()
        api_model_validation.validate(model, error_context)
        self.assertTrue(error_context.has_errors())
        self.assertEqual(1, len(error_context.errors))
        self.assertHasError(error_context, vals.CommonErrorCodes.DUPLICATE_VALUE,
            'field_with_unique_child_field_constraint[4].string_field')

    def test_range_constraints(self):
        model = ModelWithRangeConstraints.new(
            min_only=4,
            max_only=11,
            min_and_max=0,
            float_min_and_max=-0.3)
        error_context = vals.ErrorContext()
        api_model_validation.validate(model, error_context)
        self.assertEqual(4, len(error_context.errors))
        self.assertHasError(error_context, vals.CommonErrorCodes.VALUE_NOT_IN_RANGE, 'min_only')
        self.assertHasError(error_context, vals.CommonErrorCodes.VALUE_NOT_IN_RANGE, 'max_only')
        self.assertHasError(error_context, vals.CommonErrorCodes.VALUE_NOT_IN_RANGE, 'min_and_max')
        self.assertHasError(error_context, vals.CommonErrorCodes.VALUE_NOT_IN_RANGE, 'float_min_and_max')

        model = ModelWithRangeConstraints.new(
            min_only=5,
            max_only=9,
            min_and_max=2,
            float_min_and_max=2)
        error_context = vals.ErrorContext()
        api_model_validation.validate(model, error_context)
        self.assertFalse(error_context.has_errors())

    def test_dependent_fields(self):
        model = ModelWithDependentFields.new(
            field1=None, field2=None)
        error_context = vals.ErrorContext()
        api_model_validation.validate(model, error_context, vals.ValidationContext())
        self.assertEqual(2, len(error_context.errors))
        self.assertHasError(error_context, vals.CommonErrorCodes.REQUIRED, 'field1')
        self.assertHasError(error_context, vals.CommonErrorCodes.REQUIRED, 'field2')

        model = ModelWithDependentFields.new(
            field1='foo', field2='bar')
        error_context = vals.ErrorContext()
        api_model_validation.validate(model, error_context, vals.ValidationContext())
        self.assertEqual(2, len(error_context.errors))
        self.assertHasError(error_context, vals.CommonErrorCodes.AMBIGUOUS, 'field1')
        self.assertHasError(error_context, vals.CommonErrorCodes.AMBIGUOUS, 'field2')

        model = ModelWithDependentFields.new(
            field1='foo', field2=None)
        error_context = vals.ErrorContext()
        api_model_validation.validate(model, error_context, vals.ValidationContext())
        self.assertEqual(0, len(error_context.errors))

        model = ModelWithDependentFields.new(
            field1=None, field2='blah')
        error_context = vals.ErrorContext()
        api_model_validation.validate(model, error_context, vals.ValidationContext())
        self.assertEqual(0, len(error_context.errors))

    def test_distinct_fields(self):
        model = ModelWithDisinctFields.new(
            field1='value1', field2='value1')
        error_context = vals.ErrorContext()
        api_model_validation.validate(model, error_context, vals.ValidationContext())
        self.assertEqual(2, len(error_context.errors))
        self.assertHasError(error_context, vals.CommonErrorCodes.REPEATED, 'field1')
        self.assertHasError(error_context, vals.CommonErrorCodes.REPEATED, 'field2')

        model = ModelWithDisinctFields.new(
            field1=None, field2='blah')
        error_context = vals.ErrorContext()
        api_model_validation.validate(model, error_context, vals.ValidationContext())
        self.assertEqual(0, len(error_context.errors))

        model = ModelWithDisinctFields.new(
            field1='foo', field2='blah')
        error_context = vals.ErrorContext()
        api_model_validation.validate(model, error_context, vals.ValidationContext())
        self.assertEqual(0, len(error_context.errors))

        model = ModelWithDisinctFields.new(
            field1=None, field2=None)
        error_context = vals.ErrorContext()
        api_model_validation.validate(model, error_context, vals.ValidationContext())
        self.assertEqual(0, len(error_context.errors))

        model = ModelWithDisinctFields.new(
            field1='', field2='')
        error_context = vals.ErrorContext()
        api_model_validation.validate(model, error_context, vals.ValidationContext())
        self.assertEqual(0, len(error_context.errors))

        model = ModelWithDisinctFields.new(
            field1='', field2=None)
        error_context = vals.ErrorContext()
        api_model_validation.validate(model, error_context, vals.ValidationContext())
        self.assertEqual(0, len(error_context.errors))

if __name__ == '__main__':
    unittest.main()
