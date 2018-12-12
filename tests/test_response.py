import unittest
from pyvies import Vies
from .vat_ids import VALID_VAT_IDS, INVALID_VAT_IDS


class colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    FAIL = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


def print_color(data, color):
    print('%s%s%s' % (color, data, colors.RESET))


class TestResponse(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestResponse, self).__init__(*args, **kwargs)
        self.vies_api = Vies()


    def test_1_valid_no_country_code(self):
        print_color('Testing valid VAT numbers (without specifying the country code)...', colors.YELLOW)

        for country_code, vat_number in VALID_VAT_IDS.items():
            vat_number = country_code + vat_number
            print_color('Testing "%s"' % vat_number, colors.BOLD)
            response = self.vies_api.request(vat_number)
            print('%s' % response)

            if response.error != 'TIMEOUT':
                self.assertEqual(response.is_valid, True)
            else:
                print_color('Request timeouted, skipping...', colors.FAIL)
            print()
        print_color('Done!', colors.GREEN)


    def test_2_valid_with_country_code(self):
        print_color('\nTesting valid VAT numbers (specifying the country code)...', colors.YELLOW)

        for country_code, vat_number in VALID_VAT_IDS.items():
            print_color('Testing "%s"' % vat_number, colors.BOLD)
            response = self.vies_api.request(vat_number, country_code)
            print('%s' % response)

            if response.error != 'TIMEOUT':
                self.assertEqual(response.is_valid, True)
            else:
                print_color('Request timeouted, skipping...', colors.FAIL)
            print()
        print_color('Done!', colors.GREEN)


    def test_3_invalid(self):
        print_color('\nTesting invalid VAT numbers (without specifying the country code)...', colors.YELLOW)

        for vat_number in INVALID_VAT_IDS:
            print_color("Testing '%s'..." % vat_number, colors.BOLD)
            response = self.vies_api.request(vat_number)
            print('%s\n' % response)

            if response.error != 'TIMEOUT':
                self.assertEqual(response.is_valid, False)
            else:
                print_color('Request timeouted, skipping...', colors.FAIL)
            print()
        print_color('Done!', colors.GREEN)


    def test_4_bypass_ratelimit(self):
        print_color('\nTesting ratelimit bypass...', colors.YELLOW)

        vat_number = 'EL094504202'

        # This first request can fail, in that case you shoould wait one minute and run it again
        print_color('Making a normal request for VAT ID "%s"...' % vat_number, colors.BOLD)
        self.vies_api = Vies()
        response = self.vies_api.request(vat_number)
        print('%s\n' % response)
        self.assertEqual(response.is_valid, True)

        print_color('Making another same request to trigger the rate limiter...', colors.BOLD)
        response = self.vies_api.request(vat_number)
        self.assertEqual(response.is_valid, False)
        print('%s\n' % response)
        self.assertEqual(response.error, response.RATELIMIT_RESPONSE)

        print_color('Bypassing ratelimit...', colors.BOLD)
        response = self.vies_api.request(vat_number, bypass_ratelimit=True)
        print('%s\n' % response)
        self.assertEqual(response.is_valid, True)

        print_color('Done!', colors.GREEN)


if __name__ == '__main__':
    unittest.main()

