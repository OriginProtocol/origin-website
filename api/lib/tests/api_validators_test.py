import decimal
import unittest

from api.lib import api_validators as vals

class ApiValidatorsTest(unittest.TestCase):
    def run_validator_test(self, validator, value, *error_codes):
        self.run_validator_test_for_method(validator, value, None, *error_codes)

    def run_validator_test_for_method(self, validator, value, method, *error_codes):
        error_context = vals.ErrorContext()
        validator.validate(value, error_context, vals.ValidationContext(method))
        if error_codes:
            self.assertTrue(error_context.has_errors())
            for error_code in error_codes:
                self.assertHasErrorCode(error_code, error_context)
        else:
            self.assertFalse(error_context.has_errors())

    def assertHasErrorCode(self, error_code, error_context):
        for error in error_context.errors:
            if error.code == error_code:
                return
        self.fail('Error code %s not found' % error_code)

    def test_type_validators(self):
        self.run_validator_test(vals.StringType(), '123')
        self.run_validator_test(vals.StringType(), u'123')
        self.run_validator_test(vals.StringType(), None)
        self.run_validator_test(vals.StringType(), 123, vals.CommonErrorCodes.INVALID_TYPE)
        self.run_validator_test(vals.StringType(), [], vals.CommonErrorCodes.INVALID_TYPE)

        self.run_validator_test(vals.IntegerType(), 123)
        self.run_validator_test(vals.IntegerType(), 123L)
        self.run_validator_test(vals.IntegerType(), -9234234234)
        self.run_validator_test(vals.IntegerType(), 0)
        self.run_validator_test(vals.IntegerType(), 0L)
        self.run_validator_test(vals.IntegerType(), None)
        self.run_validator_test(vals.IntegerType(), '123', vals.CommonErrorCodes.INVALID_TYPE)
        self.run_validator_test(vals.IntegerType(), u'123', vals.CommonErrorCodes.INVALID_TYPE)
        self.run_validator_test(vals.IntegerType(), 123.0, vals.CommonErrorCodes.INVALID_TYPE)
        self.run_validator_test(vals.IntegerType(), '', vals.CommonErrorCodes.INVALID_TYPE)
        self.run_validator_test(vals.IntegerType(), [], vals.CommonErrorCodes.INVALID_TYPE)

        self.run_validator_test(vals.DecimalIntegerType(), decimal.Decimal(123))
        self.run_validator_test(vals.DecimalIntegerType(), decimal.Decimal(0))
        self.run_validator_test(vals.DecimalIntegerType(), None)
        self.run_validator_test(vals.DecimalIntegerType(), decimal.Decimal('23.00'))
        self.run_validator_test(vals.DecimalIntegerType(), decimal.Decimal('23.'))
        self.run_validator_test(vals.DecimalIntegerType(), decimal.Decimal(-3234))
        self.run_validator_test(vals.DecimalIntegerType(), 123, vals.CommonErrorCodes.INVALID_TYPE)
        self.run_validator_test(vals.DecimalIntegerType(), '123', vals.CommonErrorCodes.INVALID_TYPE)
        self.run_validator_test(vals.DecimalIntegerType(), decimal.Decimal('23.50'), vals.CommonErrorCodes.INVALID_TYPE)
        self.run_validator_test(vals.DecimalIntegerType(), decimal.Decimal('-0.00001'), vals.CommonErrorCodes.INVALID_TYPE)

        self.run_validator_test(vals.FloatType(), 1.0)
        self.run_validator_test(vals.FloatType(), 1.25)
        self.run_validator_test(vals.FloatType(), 0.0)
        self.run_validator_test(vals.FloatType(), 0.1)
        self.run_validator_test(vals.FloatType(), 123)
        self.run_validator_test(vals.FloatType(), 123L)
        self.run_validator_test(vals.FloatType(), -9234234234)
        self.run_validator_test(vals.FloatType(), 0)
        self.run_validator_test(vals.FloatType(), 0L)
        self.run_validator_test(vals.FloatType(), None)
        self.run_validator_test(vals.FloatType(), '123', vals.CommonErrorCodes.INVALID_TYPE)
        self.run_validator_test(vals.FloatType(), u'123', vals.CommonErrorCodes.INVALID_TYPE)
        self.run_validator_test(vals.FloatType(), '', vals.CommonErrorCodes.INVALID_TYPE)
        self.run_validator_test(vals.FloatType(), [], vals.CommonErrorCodes.INVALID_TYPE)

        self.run_validator_test(vals.BooleanType(), True)
        self.run_validator_test(vals.BooleanType(), False)
        self.run_validator_test(vals.BooleanType(), None)
        self.run_validator_test(vals.BooleanType(), 0, vals.CommonErrorCodes.INVALID_TYPE)
        self.run_validator_test(vals.BooleanType(), '', vals.CommonErrorCodes.INVALID_TYPE)
        self.run_validator_test(vals.BooleanType(), [], vals.CommonErrorCodes.INVALID_TYPE)
        self.run_validator_test(vals.BooleanType(), {}, vals.CommonErrorCodes.INVALID_TYPE)
        self.run_validator_test(vals.BooleanType(), 123, vals.CommonErrorCodes.INVALID_TYPE)
        self.run_validator_test(vals.BooleanType(), u'hello', vals.CommonErrorCodes.INVALID_TYPE)

    def test_required_validator(self):
        self.run_validator_test(vals.Required(), None, vals.CommonErrorCodes.REQUIRED)
        self.run_validator_test(vals.Required(), '', vals.CommonErrorCodes.REQUIRED)
        self.run_validator_test(vals.Required(), u'', vals.CommonErrorCodes.REQUIRED)
        self.run_validator_test(vals.Required(), [], vals.CommonErrorCodes.REQUIRED)
        self.run_validator_test(vals.Required(), {}, vals.CommonErrorCodes.REQUIRED)
        self.run_validator_test(vals.Required(), 'abc')
        self.run_validator_test(vals.Required(), 123)
        self.run_validator_test(vals.Required(), 0)
        self.run_validator_test(vals.Required(), 0.0)
        self.run_validator_test(vals.Required(), u'abc')
        self.run_validator_test(vals.Required(), ['abc'])
        self.run_validator_test(vals.Required(), [1, 2, 3])
        self.run_validator_test(vals.Required(), [None])

        self.run_validator_test_for_method(vals.Required(['insert']), None, 'insert', vals.CommonErrorCodes.REQUIRED)
        self.run_validator_test_for_method(vals.Required(['insert']), '', 'insert', vals.CommonErrorCodes.REQUIRED)
        self.run_validator_test_for_method(vals.Required(['insert']), [], 'insert', vals.CommonErrorCodes.REQUIRED)
        self.run_validator_test_for_method(vals.Required(['insert']), {}, 'insert', vals.CommonErrorCodes.REQUIRED)
        self.run_validator_test_for_method(vals.Required(['insert']), None, 'update')
        self.run_validator_test_for_method(vals.Required(['insert']), [], 'update')
        self.run_validator_test_for_method(vals.Required(['insert']), {}, 'update')
        self.run_validator_test_for_method(vals.Required(['insert']), 123, 'insert')
        self.run_validator_test_for_method(vals.Required(['insert']), 'abc', 'insert')
        self.run_validator_test_for_method(vals.Required(['insert']), [1], 'insert')

if __name__ == '__main__':
    unittest.main()
