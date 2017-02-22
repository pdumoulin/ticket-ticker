
from pprint import pformat
from api_client import StubHubAPIClient

c = StubHubAPIClient('conf/conf.json')

def test_events():
    params = {
        'q' : 'New York Rangers',
        'city' : 'New York',
        'rows' : 500,
        'parking' : False,
        'minAvailableTickets' : 2,
    }
    (code, results) = c.get_events(params)
    print code
    if code == 200:
        events = results['events']
        for event in events:
            if event['status'] == 'Active':
                print event['name']
                print event['id']
                print "%s://www.%s/%s" % ('https', 'stubhub.com', event['webURI'])
                print event['eventDateLocal']
                print event['status']
                print event['ticketInfo']
                print ""
        print results['numFound']
    else:
        print results


def test_inventory(event_id):
    (code, results) = c.get_listings(
        event_id,
        {
            'priceMax' : 250,
            'quantity' : 2,
            'sort' : 'currentprice'
        }
    )
    print code
    if code == 200:
        listings = results.get('listings', [])
        for listing in listings:
            categories = result.get('listingAttributeCategoryList', [])
            if 1 in categories:
                print "NOPE!!"
            print pformat(listing)
            print ""
    else:
        print results

# test_events()

# MTL
# test_inventory(9606227)

# CBJ
# test_inventory(9606217)

