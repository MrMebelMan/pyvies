#!/usr/bin/env python3

from requests import post as requests_post
from bs4 import BeautifulSoup as Soup

NoneType = type(None)


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


    def __init__(self, bypass_ratelimit=False):
        # a switch to bypass the 1 minute API ban after sending the same data twice
        # API returns valid=False correctly for invalid requests, even when ratelimited
        # The idea is to exploit this behaviour by first sending the invalid request for the same country,
        # making sure that server returned the correct valid=False response,
        # and then continuing to check the real VAT ID, considering ratelimit error as success
        self.bypass_ratelimit = bypass_ratelimit


    def request(self, vat_id: (str, NoneType), country_code: (str, NoneType) = None):
        allowed_arg_types = (NoneType, str)

        if not isinstance(vat_id, allowed_arg_types):
            raise TypeError('vat_id should be either str, or NoneType')
        elif not isinstance(country_code, allowed_arg_types):
            raise TypeError('country_code should be either str, or NoneType')

        country_code = country_code.upper() if type(country_code) is str else country_code

        vat_id = vat_id.lstrip().rstrip().upper() if vat_id else ''
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

        request.country_code = country_code
        request.vat_id = vat_id
        request.post(self.bypass_ratelimit)

        return request


class ViesRequest:
    RATELIMIT_RESPONSE = 'MS_UNAVAILABLE'
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


    def validate(self, bypass_ratelimit=False):
        self.soup = Soup(self.response.text, 'xml')
        self.is_valid = self.get_tag_text('valid') == 'true'

        if bypass_ratelimit and self.error == self.RATELIMIT_RESPONSE:
            self.error = False
            self.is_valid = True
            return  # we will not get the company name and address from ratelimited response anyway

        self.company_name = self.get_tag_text('name', optional=True)
        if self.company_name:
            self.company_name = self.company_name.replace('---', '') or None

        self.company_address = self.get_tag_text('address', optional=True)
        if self.company_address:
            self.company_address = self.company_address.replace('---', '') or None


    def post(self, bypass_ratelimit=False):
        headers = {'Content-type': 'text/xml'}

        xml_request = '' \
        '<?xml version="1.0" encoding="UTF-8"?>' \
        '<SOAP-ENV:Envelope ' \
        'xmlns:ns0="urn:ec.europa.eu:taxud:vies:services:checkVat:types" ' \
        'xmlns:ns1="http://schemas.xmlsoap.org/soap/envelope/" ' \
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' \
        'xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">' \
        '<SOAP-ENV:Header/>' \
        '<ns1:Body>' \
        '<ns0:checkVat>' \
        '<ns0:countryCode>%s</ns0:countryCode>' \
        '<ns0:vatNumber>%s</ns0:vatNumber>' \
        '</ns0:checkVat>' \
        '</ns1:Body>' \
        '</SOAP-ENV:Envelope>'

        self.data = xml_request % (self.country_code, self.vat_id)

        if bypass_ratelimit:
            data = xml_request % (self.country_code, '1337')
            self.response = requests_post(url=self.url, data=data, headers=headers)

            self.validate()
            if self.error:
                return  # The server is down, do not try to send the real request

        self.response = requests_post(url=self.url, data=self.data, headers=headers)
        self.validate(bypass_ratelimit)

