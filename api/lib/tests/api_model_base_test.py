import unittest

from api.lib import api_model_base

class ChildModel(api_model_base.Model):
    child_string_field = api_model_base.StringField('child_string_field')
    child_int_field = api_model_base.IntegerField('child_int_field')

class ParentModel(api_model_base.Model):
    string_field = api_model_base.StringField('string_field')
    int_field = api_model_base.IntegerField('int_field')
    float_field = api_model_base.FloatField('float_field')
    bool_field = api_model_base.BooleanField('bool_field')
    empty_field = api_model_base.StringField('empty_field')
    model_field = api_model_base.ModelField('model_field', ChildModel)
    string_list_field = api_model_base.ListField('string_list_field', unicode)
    model_list_field = api_model_base.ListField('model_list_field', ChildModel)
    arbitrary_dict_field = api_model_base.DictField('arbitrary_dict_field', lambda x: x)
    model_dict_field = api_model_base.DictField('model_dict_field', ChildModel)

class BaseModel(api_model_base.Model):
    base_field = api_model_base.StringField('base_field')

class SubclassModel(BaseModel):
    subclass_field = api_model_base.StringField('subclass_field')

class ApiModelValidationTest(unittest.TestCase):
    def test_create_using_new(self):
        m = ParentModel.new(
            string_field='string field value',
            int_field=123,
            float_field=1.25,
            bool_field=True,
            model_field=ChildModel.new(
                child_string_field='child string field value',
                child_int_field=989),
            string_list_field=['a', 'b', 'c'],
            model_list_field=[ChildModel.new(child_string_field='blah', child_int_field=222)],
            arbitrary_dict_field={'key1': 'value1', 'key2': [1, 3, 2]},
            model_dict_field={'modelkey1': ChildModel.new(child_string_field='asdfasdf')})
        self.assertEqual('string field value', m.string_field)
        self.assertEqual(123, m.int_field)
        self.assertEqual(1.25, m.float_field)
        self.assertEqual(True, m.bool_field)
        self.assertTrue(isinstance(m.model_field, ChildModel))
        self.assertEqual('child string field value', m.model_field.child_string_field)
        self.assertEqual(989, m.model_field.child_int_field)
        self.assertListEqual(['a', 'b', 'c'], m.string_list_field)
        self.assertEqual(1, len(m.model_list_field))
        self.assertTrue(isinstance(m.model_list_field[0], ChildModel))
        self.assertEqual('blah', m.model_list_field[0].child_string_field)
        self.assertEqual(222, m.model_list_field[0].child_int_field)
        self.assertDictEqual({'key1': 'value1', 'key2': [1, 3, 2]}, m.arbitrary_dict_field)
        self.assertEqual(1, len(m.model_dict_field.items()))
        self.assertTrue(isinstance(m.model_dict_field['modelkey1'], ChildModel))
        self.assertEqual('asdfasdf', m.model_dict_field['modelkey1'].child_string_field)
        self.assertIsNone(m.empty_field)

        raw = {
            'arbitrary_dict_field': {'key1': 'value1', 'key2': [1, 3, 2]},
            'bool_field': True,
            'float_field': 1.25,
            'int_field': 123,
            'model_dict_field': {'modelkey1': {'child_string_field': 'asdfasdf'}},
            'model_field': {'child_int_field': 989,
                            'child_string_field': 'child string field value'},
            'model_list_field': [{'child_int_field': 222, 'child_string_field': 'blah'}],
            'string_field': 'string field value',
            'string_list_field': ['a', 'b', 'c'],
        }
        self.assertDictEqual(raw, m.raw)

    def test_subclassing(self):
        m = SubclassModel.new(
            subclass_field='subclass value',
            base_field='base value')
        self.assertEqual('subclass value', m.subclass_field)
        self.assertEqual('base value', m.base_field)

    def test_update_from_other_model(self):
        m = ParentModel.new(
            string_field='original value',
            int_field=123,
            float_field=42.0,
            model_field=ChildModel.new(
                child_string_field='original child value'))
        m.update(ParentModel.new(
            string_field='new value',
            int_field=456,
            model_field=ChildModel.new(
                child_string_field='new child value',
                child_int_field=987)))
        self.assertEqual('new value', m.string_field)
        self.assertEqual(456, m.int_field)
        self.assertEqual('new child value', m.model_field.child_string_field)
        self.assertEqual(987, m.model_field.child_int_field)
        self.assertEqual(42.0, m.float_field)

    def test_model_printing(self):
        m = ParentModel.new(
            string_field='string field value',
            int_field=123,
            float_field=1.25,
            bool_field=True,
            model_field=ChildModel.new(
                child_string_field='child string field value',
                child_int_field=989),
            string_list_field=['a', 'b', 'c'],
            model_list_field=[ChildModel.new(child_string_field='blah', child_int_field=222)],
            arbitrary_dict_field={'key1': 'value1', 'key2': [1, 3, 2]},
            model_dict_field={'modelkey1': ChildModel.new(child_string_field='asdfasdf')})
        str_value = \
'''<class ParentModel>
    arbitrary_dict_field: {
        key2:  [
            1,
            3,
            2,
        ]
        key1:  'value1'
    }
    bool_field: True
    float_field: 1.25
    int_field: 123
    model_dict_field: {
        modelkey1:  <class ChildModel>
            child_string_field: 'asdfasdf'
    }
    model_field: <class ChildModel>
        child_int_field: 989
        child_string_field: 'child string field value'
    model_list_field: [
        <class ChildModel>
            child_int_field: 222
            child_string_field: 'blah',
    ]
    string_field: 'string field value'
    string_list_field: [
        u'a',
        u'b',
        u'c',
    ]'''
        for expected, actual in zip(str_value.split('\n'), str(m).split('\n')):
            self.assertEqual(expected, actual)

    def test_model_printing_for_subclasses(self):
        m = SubclassModel.new(
            subclass_field='subclass value',
            base_field='base value')
        str_value = \
'''<class SubclassModel>
    base_field: 'base value'
    subclass_field: 'subclass value'
'''
        for expected, actual in zip(str_value.split('\n'), str(m).split('\n')):
            self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
