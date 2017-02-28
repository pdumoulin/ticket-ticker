
from pprint import pformat

import json
import requests

class APIException(Exception):
    
    def __init__(self, code, message):
        super(Exception, self).__init__(message)
        self.code = code

class StubHubAPIClient(object):


    def __init__(self, access_token, endpoint):
        self.access_token = access_token
        self.endpoint = endpoint

    def get_events(self, search):
        (code, results) = self._call(
            'GET', 
            'search/catalog/events/v3', 
            {
                'q'       : search,
                'rows'    : 500,
                'parking' : False,
                'sort'    : 'eventDateLocal'
            }
        )
        if code != 200:
            raise APIException(code, 'error on get_events() %s' % code)
        events = []
        for event in results['events']:
            events.append(Event(event))
        return events

    # needed to request special access apisupport@stubhub.com
    def get_listings(self, event_id, quantity, max_price):
        (code, results) = self._call(
            'GET',
            'search/inventory/v2',
            {
                'eventid'  : event_id,
                'quantity' : quantity,
                'priceMax' : max_price,
                'sort'     : 'currentprice'
            }
        )
        if code != 200:
            raise APIException(code, 'error on get_listings() %s' % code)
        listings = []
        for listing in results.get('listing', []):
            listings.append(Listing(listing))
        return listings

    def _call(self, verb, route, params, auth=True):
        headers  = { 'Accept' : 'application/json' }
        if auth:
            headers['Authorization'] = "Bearer %s" % self.access_token
        req = requests.Request(
            verb,
            self.endpoint + route, 
            headers=headers,
            params=params
        )
        prepared = req.prepare()
        s = requests.Session()
        response = s.send(prepared)
        body = response.content
        try:
            body = json.loads(body)
        except:
            pass
        return (response.status_code, body)


class Event(object):

    def __init__(self, event):
        self.token = event['id']
        self.name = event['name']

        self.date = event['eventDateLocal']
        self.status = event['status'].lower()

        self.uri = event['webURI']
        self.url = None
        self.set_url()

        self.attributes = event['attributes']
        self.act_primary = self._extract_attribute('act_primary')
        self.act_secondary = self._extract_attribute('act_secondary')
       
        self.tickets = []

    def _extract_attribute(self, name):
        for attribute in self.attributes:
            if attribute['name'] == name:
                return attribute['value'].lower()
        return None    

    def set_url(self, quantity=None, exclude=[]):
        self.url = 'https://www.stubhub.com/%s' % self.uri
        if quantity is not None:
            self.url += '&qty=%s' % quantity
        if len(exclude) > 0:
            self.url +='&excl=%s' % ','.join([str(x) for x in exclude])

    def output(self):
        return '\n'.join([
                self.name,
                self.date,
                self.url,
                '\n'
            ])

class Listing(object):

    OBSTRUCTED = 1
    WHEERL_CHAIR = 2
    ALCOHOL_FREE = 3
    PARKING_INC = 4
    PIGGY_BACK = 5
    AISLE = 6

    def __init__(self, listing):
        self.token = listing['listingId']
        self.quantity = listing['quantity']
        self.full_price = listing['currentPrice']['amount']
        self.list_price = listing['listingPrice']['amount']
        self.row = listing['row']
        self.seats = listing['seatNumbers'].split(',')
        self.section = listing['sectionName']
        self.categories = listing.get('listingAttributeCategoryList', [])

    def output(self):
        return '\n'.join([
                '########################################',
                'Token:   %s' % self.token,
                'Section: %s' % self.section,
                'Row:     %s' % self.row,
                'Seats:   %s' % ','.join([str(x) for x in self.seats]),
                '----------------------------------------',
                'Each:    %s' % self.full_price,
                'Total:   %s' % (self.quantity * self.full_price),
                '\n'
            ])
        
