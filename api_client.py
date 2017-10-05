
import json
import requests
import base64

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

        # filter out weird events w/o home-away info
        events = results['events']
        events = filter(lambda e: 'performersCollection' in e, events)
        events = filter(lambda e: len(e['performersCollection']) == 2, events)
        return [Event(e) for e in events]

    # needed to request special access apisupport@stubhub.com
    def get_listings(self, event_token, quantity, max_price):
        (code, results) = self._call(
            'GET',
            'search/inventory/v2',
            {
                'eventid'  : event_token,
                'quantity' : quantity,
                'priceMax' : max_price,
                'sort'     : 'currentprice'
            }
        )
        if code != 200:
            raise APIException(code, 'error on get_listings() %s' % code)
        return [Listing(event_token, l) for l in results.get('listing', [])]

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
        self.venue = event['venue']['name']

        self.date = event['eventDateLocal']
        self.status = event['status'].lower()

        self.uri = event['webURI']
        self.url = None
        self.set_url()

        # handle super-ugly data to determine home and away teams
        away_index = 0 if event['performersCollection'][0].get('role', None) == 'AWAY_TEAM' else 1
        home_index = 0 if away_index == 1 else 1
        self.act_primary = event['performersCollection'][home_index]['name'].lower()
        self.act_secondary = event['performersCollection'][away_index]['name'].lower()

        self.tickets = []

    def set_url(self, quantity=None, exclude=[], max_price=None):
        self.url = 'https://www.stubhub.com/%s?priceWithFees=true&sort=price+asc' % self.uri
        if max_price is not None:
            self.url += '&sliderMax=0,%s' % max_price
        # if quantity is not None:
        #     self.url += '&qty=%s' % quantity
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

    def __init__(self, event_token, listing):
        self.event_token = event_token
        self.token = listing['listingId']
        self.quantity = listing['quantity']
        self.full_price = listing['currentPrice']['amount']
        self.list_price = listing['listingPrice']['amount']
        self.row = listing['row']
        self.seats = listing.get('seatNumbers', '').split(',')
        self.section = listing['sectionName']
        self.categories = listing.get('listingAttributeCategoryList', [])

    def uid(self):
        return base64.b64encode(':'.join(str(x) for x in [
                self.event_token,
                self.token,
                self.full_price
            ]))

    def output(self):
        return '\n'.join([
                '########################################',
                'Token:   %s' % self.token,
                'Section: %s' % self.section,
                'Row:     %s' % self.row,
                'Seats:   %s' % ','.join([str(x) for x in self.seats]),
                'Aisle:   %s' % str(Listing.AISLE in self.categories),
                '----------------------------------------',
                'Each:    %s' % self.full_price,
                'Total:   %s' % (self.quantity * self.full_price),
                '\n'
            ])
        
