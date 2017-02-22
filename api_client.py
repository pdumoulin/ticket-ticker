
from pprint import pformat

import json
import requests

class StubHubAPIClient(object):

    def __init__(self, config_filename):
        with open(config_filename) as config_file:
            config = json.load(config_file)
            self.access_token = config.get('access_token', None)
            self.endpoint = config.get('endpoint', None)

    def get_events(self, params={}):
        params['sort'] = 'eventDateLocal'
        return self._call(
            'GET', 
            'search/catalog/events/v3', 
            params
        )

    # needed to request special access apisupport@stubhub.com
    def get_listings(self, event_id, params={}):
        params['eventid'] = event_id
        return self._call(
            'GET',
            'search/inventory/v2',
            params
        )

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

