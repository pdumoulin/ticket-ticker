
from pprint import pformat

import json
import requests

class StubHubAPIClient(object):

    def __init__(self, config_filename):
        with open(config_filename) as config_file:
            config = json.load(config_file)
            self.access_token = config.get('access_token', None)
            self.endpoint = config.get('endpoint', None)

    def get_events(self, search, params={}):
        params['q'] = search
        params['sort'] = 'eventDateLocal'
        params['rows'] = 500
        params['parking'] = False
        (code, results) = self._call(
            'GET', 
            'search/catalog/events/v3', 
            params
        )
        if code != 200:
            raise Exception('non-200 response on get_events() : %s' % code)

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
    def get_listings(self, event_id, quantity, max_price, params={}):
        params['eventid'] = event_id
        params['sort'] = 'currentprice'
        params['quantity'] = quantity
        params['priceMax'] = max_price
        (code, results) = self._call(
            'GET',
            'search/inventory/v2',
            params
        )
        if code != 200:
            raise Exception('non-200 response on get_listings() : %s' % code)
        tickets = []
        for listing in results.get('listing', []):
            categories = listing.get('listingAttributeCategoryList', [])
            tickets.append({
                'id'         : listing['listingId'],
                'full_price' : listing['currentPrice']['amount'],
                'list_price' : listing['listingPrice']['amount'],
                'quantity'   : listing['quantity'],
                'row'        : listing['row'],
                'seats'      : listing['seatNumbers'].split(','),
                'section'    : listing['sectionName'],
                'obstructed' : 1 in categories,
                'piggy_back' : 5 in categories
            })
            pass
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

