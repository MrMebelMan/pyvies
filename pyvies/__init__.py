#!/usr/bin/env python3

from requests import post as requests_post
from bs4 import BeautifulSoup as Soup

class Vies:
    # ISO 3166-1 alpha-2 country codes.
    EU_COUNTRY_CODES = set([
        'AT',  # Austria.
        'BE',  # Belgium.
        'BG',  # Bulgaria.
        'CY',  # Cyprus.
        'CZ',  # Czech Republic.
        'DE',  # Germany.
        'DK',  # Denmark.
        'EE',  # Estonia.
        'ES',  # Spain.
        'FI',  # Finland.
        'FR',  # France.
        'GB',  # United Kingdom.
        'EL',  # Greece.
        'HR',  # Croatia.
        'HU',  # Hungary.
        'IE',  # Ireland.
        'IT',  # Italy.
        'LT',  # Lithuania.
        'LU',  # Luxembourg.
        'LV',  # Latvia.
        'MT',  # Malta.
        'NL',  # Netherlands.
        'PL',  # Poland.
        'PT',  # Portugal.
        'RO',  # Romania.
        'SE',  # Sweden.
        'SI',  # Slovenia.
        'SK',  # Slovakia.
    ])

    def request(self, vat_id: str, country_code: str = None):
        country_code = country_code.upper() if type(country_code) is str else country_code
        vat_id = vat_id.lstrip().rstrip().upper()
        vat_id = ''.join([c for c in vat_id if c not in '\t -'])

        request = ViesRequest(vat_id, country_code)

        if len(vat_id) <= 8:
            request.error = 'vat_id (%s) is too short' % vat_id
        elif country_code and vat_id[:2] == country_code:
            vat_id = vat_id[2:]
        elif not country_code:
            country_code, vat_id = vat_id[:2], vat_id[2:]

        if len(country_code) != 2:
            request.error = 'country code (%s) should be 2 characters long' % country_code
        elif any(c.isdigit() for c in country_code):
            request.error = 'country code (%s) cannot contain digits' % country_code
        elif country_code not in self.EU_COUNTRY_CODES:
            request.error = 'unsupported country code: "%s"' % country_code
        
        if request.error:
            request.is_valid = False
            return request

        request = ViesRequest(vat_id, country_code)
        request.post()

        return request


class ViesRequest:
    url = 'http://ec.europa.eu/taxation_customs/vies/services/checkVatService'

    def __init__(self, vat_id: str, country_code: str):
        self.vat_id = vat_id
        self.country_code = country_code
        self.is_valid = None
        self.company_name = None
        self.company_address = None
        self.data = None
        self.response = None
        self.error = None


    def __str__(self):
        if self.is_valid is None:
            validity = 'not validated'
        elif self.is_valid:
            validity = 'valid'
        else:
            validity = 'invalid'

        country_code = self.country_code or ''
        vat_id = self.vat_id or ''

        ret = 'VAT number "%s%s" (%s)' % (country_code, vat_id, validity)
        if self.error:
            ret += ', error: %s' % self.error

        return ret


    @property
    def pretty(self):
        if self.response:
            return self.soup.prettify()


    def save_error(self):
        error_attr = self.soup.find('faultstring')
        if error_attr:
            self.error = error_attr.text


    def get_tag_text(self, name: str, optional: bool = False):
        tag = self.soup.find(name)
        if not tag:
            if not optional:
                self.is_valid = False
                self.save_error()
            return None
        else:
            return tag.text


    def validate(self):
        self.is_valid = self.get_tag_text('valid') == 'true'

        self.company_name = self.get_tag_text('name', optional=True)
        if self.company_name:
            self.company_name = self.company_name.replace('---', '') or None

        self.company_address = self.get_tag_text('address', optional=True)
        if self.company_address:
            self.company_address = self.company_address.replace('---', '') or None


    def post(self):
        headers = {'Content-type': 'text/xml'}

        self.data = '' \
        '<?xml version="1.0" encoding="UTF-8"?>' \
        '<SOAP-ENV:Envelope ' \
        'xmlns:ns0="urn:ec.europa.eu:taxud:vies:services:checkVat:types" ' \
        'xmlns:ns1="http://schemas.xmlsoap.org/soap/envelope/" ' \
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' \
        'xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">' \
        '<SOAP-ENV:Header/>' \
        '<ns1:Body>' \
        '<ns0:checkVat>' \
        '<ns0:countryCode>' + self.country_code + '</ns0:countryCode>' \
        '<ns0:vatNumber>' + self.vat_id + '</ns0:vatNumber>' \
        '</ns0:checkVat>' \
        '</ns1:Body>' \
        '</SOAP-ENV:Envelope>'

        self.response = requests_post(url=self.url, data=self.data, headers=headers)
        self.soup = Soup(self.response.text, 'xml')
        self.validate()


