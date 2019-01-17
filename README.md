# PyVIES
A simple Python3 API wrapper for VIES VAT number validation (with ratelimit bypass feature).

Some countries (IT, EL), will ratelimit your requests if you send the same data twice.
There is a workaround, but it should be used with extreme caution. See ViesRequest code comments for details.

# Usage

```python
from pyvies import Vies

vies_api = Vies()

vat_id = 'qwertyuiop'  # with or without the country code prefix
country_code = 'WL'  # optional, will be used if no prefix found in vat_id
bypass_ratelimit = True  # use a workaround to bypass API ban (optional, dangerous)

request = vies_api.request(vat_id, country_code, bypass_ratelimit)
if request.is_valid:
    print('%s is a valid VAT!' % vat_id)
    print('%s\n%s' % (request.company_name, request.company_address))
else:
    print('%s is an invalid VAT!' % vat_id)
    print(request.error)
```
# Tests
To run all tests:
```bash
python3 -m unittest tests/test_*.py
```
or simply:
```bash
./run_tests.sh
```
# Disclaimer
This is not a hack, just a different interpretation of server's response.

It's important to mention that VIES is not ratelimiting by IP - it blocks the whole country globally for everyone instead :trollface:
