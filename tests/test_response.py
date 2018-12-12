import unittest
from pyvies import Vies
from .vat_ids import VALID_VAT_IDS, INVALID_VAT_IDS


class TestResponse(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestResponse, self).__init__(*args, **kwargs)
        self.vies_api = Vies()

    def test_1_valid_no_country_code(self):
        print('Testing valid VAT numbers (without specifying the country code)...')
        for vat_number in VALID_VAT_IDS:
            print('Testing "%s"' % vat_number)
            response = self.vies_api.request(vat_number)
            print('%s' % response)

            if response.error != 'TIMEOUT':
                self.assertEqual(response.is_valid, True)
            else:
                print('Request timeouted, skipping...')
            print()

    def test_2_invalid(self):
        print('Testing invalid VAT numbers (without specifying the country code)...')
        for vat_number in INVALID_VAT_IDS:
            print("Testing '%s'..." % vat_number)
            response = self.vies_api.request(vat_number)
            print('%s\n' % response)

            if response.error != 'TIMEOUT':
                self.assertEqual(response.is_valid, False)
            else:
                print('Request timeouted, skipping...')
            print()


if __name__ == '__main__':
    unittest.main()

