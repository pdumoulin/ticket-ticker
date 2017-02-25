
from pprint import pformat

import json
import requests

class APIException(Exception):
    
    def __init__(self, code, message):
        super(Exception, self).__init__(message)
        self.code = code

class StubHubAPIClient(object):

    CATEGORIES = {
        'obstructed'   : 1,
        'wheelchair'   : 2,
        'alcohol_free' : 3,
        'parking_inc'  : 4,
        'piggy_back'   : 5,
        'aisle'        : 6
    }

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
            event_dict = {
                'id'        : event['id'],
                'name'      : event['name'],
                'date'      : event['eventDateLocal'],
                'status'    : event['status'].lower(),
                'url'       : 'https://www.stubhub.com/%s' % event['webURI']
            }
            extra_attributes = ['act_primary', 'act_secondary']
            for attr in extra_attributes:
                event_dict[attr] = ''
            for attr in event['attributes']:
                if attr['name'] in extra_attributes:
                    event_dict[attr['name']] = attr['value'].lower()
            events.append(event_dict)
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
        tickets = []
        for listing in results.get('listing', []):
            tickets.append({
                'id'         : listing['listingId'],
                'full_price' : listing['currentPrice']['amount'],
                'list_price' : listing['listingPrice']['amount'],
                'quantity'   : listing['quantity'],
                'row'        : listing['row'],
                'seats'      : listing['seatNumbers'].split(','),
                'section'    : listing['sectionName'],
                'categories' : listing.get('listingAttributeCategoryList', [])
            })
        return tickets

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

