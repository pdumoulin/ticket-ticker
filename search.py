
import argparse

from pprint import pformat
from api_client import StubHubAPIClient
c = StubHubAPIClient('conf/conf.json')

# TODO - handle 429s gracefully

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-q', required=True, type=int, help='number of tickets to search for')
    parser.add_argument('-p', required=True, type=float, help='max price per ticket in dollars and cents')
    parser.add_argument('-l', required=False, type=int, default=None, help='limit number of events')
    parser.add_argument('--home', required=False, type=str, default='', help='home team name')
    parser.add_argument('--away', required=False, type=str, default='', help='away team name')
    parser.add_argument('-d', required=False, type=str, help='date of game (YYYY-MM-DD)')
    args = parser.parse_args()
    
    # variable args
    quantity = args.q
    max_price = args.p
    home_team = args.home.lower()
    away_team = args.away.lower()
    event_limit = args.l
    date = args.d

    # static filtering args
    event_status = 'active'
    obstructed = False
    piggy_back = False

    # get events based on home and away team name
    search = ("%s %s" % (home_team, away_team)).title()
    events = c.get_events(search)
    events = filter(lambda e: e['status'] == event_status, events)

    # filter out false positives from search term
    if home_team != '':
        events = filter(lambda e: home_team in e['act_primary'], events)
    if away_team != '':
        events = filter(lambda e: away_team in e['act_secondary'], events)

    # limit results to minimize ticket fetch requests
    if event_limit is not None:
        events = events[0:event_limit]

    # go through events to find tickets
    for event in events:
        # TODO - print event header
        print event['name']
        continue

        tickets = c.get_listings(event['id'], quantity, max_price)
        if not obstructed:
            tickets = filter(lambda t: t['obstructed'] == True, tickets)
        if not piggy_back:
            tickets = filter(lambda t: t['piggy_back'] == True, tickets)
        for ticket in tickets:
            # TODO - print some data
            pass

if __name__ == '__main__':
    main()


