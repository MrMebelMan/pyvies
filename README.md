# PyVIES
A simple Python3 API wrapper for VIES VAT number validation.

# Usage

```python
from pyvies import Vies


vies_api = Vies()

vat_id = 'qwertyuiop'  # with or without the country code prefix
country_code = 'WL'  # optional, will be used if no prefix found in vat_id

request = vies_api.request(vat_id, country_code)
if request.is_valid:
    print('%s is a valid VAT!' % vat_id)
    print(request.company_name)
    print(request.company_address)
else:
    print('%s is an invalid VAT!' % vat_id)
    print(request.error)
```
