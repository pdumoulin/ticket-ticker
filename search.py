
import time
import json
import argparse

from pprint import pformat
from api_client import StubHubAPIClient, APIException
from mail_client import EmailClient

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-q', required=True, type=int, help='number of tickets to search for')
    parser.add_argument('-p', required=True, type=float, help='max price per ticket in dollars and cents')
    parser.add_argument('-l', required=False, type=int, default=None, help='limit number of events')
    parser.add_argument('--date', required=False, type=str, default='', help='date of game (YYYY-MM-DD)')
    parser.add_argument('--home', required=False, type=str, default='', help='home team name')
    parser.add_argument('--away', required=False, type=str, default='', help='away team name')
    parser.add_argument('--conf', required=False, type=str, default='./conf/conf.json', help='config file loc')
    parser.add_argument('--email', required=False, type=str, default=None, help='email to send results to')
    args = parser.parse_args()

    # variable args
    quantity = args.q
    max_price = args.p
    home_team = args.home.lower()
    away_team = args.away.lower()
    event_limit = args.l
    date = args.date
    config_filename = args.conf
    email = args.email

    # process config file and setup clients
    with open(config_filename) as config_file:
        config = json.load(config_file)
        c = StubHubAPIClient(config['access_token'], config['endpoint'])
        if email is not None:
            email_client = EmailClient(config['email']['sender'], config['email']['password'])

    # static filtering args
    event_status = 'active'
    exclude = [
        StubHubAPIClient.CATEGORIES['obstructed'], 
        StubHubAPIClient.CATEGORIES['piggy_back']
    ]

    # get events based on home and away team name
    search = ("%s %s" % (home_team, away_team)).title()
    events = request(c.get_events, search)

    # filter out events by status
    events = filter(lambda e: e['status'] == event_status, events)

    # filter out optional params
    if home_team != '':
        events = filter(lambda e: home_team in e['act_primary'], events)
    if away_team != '':
        events = filter(lambda e: away_team in e['act_secondary'], events)
    if date != '':
        events = filter(lambda e: date in e['date'], events)

    # limit results to minimize ticket fetch requests
    if event_limit is not None:
        events = events[0:event_limit]

    # go through events to find tickets
    for event in events:
        
        # tailor event url to query params
        event['url'] += '?priceWithFees=true&sort=price+asc'
        event['url'] += '&qty=%s' % quantity
        if len(exclude) > 0:
            event['url'] += '&excl=%s' % ','.join([str(x) for x in exclude])

        # get tickets for the event
        tickets = request(c.get_listings, event['id'], quantity, max_price)

        # filter out tickets with bad properties
        tickets = filter(lambda t: len(list(set(exclude) & set(t['categories']))) == 0, tickets)

        # add ticket to the event
        event['tickets'] = tickets

    # deal with sending output
    for event in events:
        if len(event['tickets']) > 0:
            if email is not None:
                email_client.send(
                    'Ticket Alert! %s : %s' % (event['name'], event['date']), 
                    event_tostring(event), 
                    email
                )
            print event_tostring(event)

def event_tostring(event):
    tickets = event['tickets']
    output = '\n'.join([
        event['name'],
        event['date'],
        event['url'],
        'Num Tickets: %s' % len(tickets),
        '\n'
    ])
    
    # TODO - add categories?

    for ticket in tickets:
        output += '\n'.join([
            '########################################',
            'Section: %s' % ticket['section'],
            'Row:     %s' % ticket['row'],
            'Seats:   %s' % ','.join(ticket['seats']),
            '----------------------------------------',
            'Each:    %s' % ticket['full_price'],
            'Total:   %s' % (ticket['quantity'] * ticket['full_price']),
            '\n'
        ])
    return output

def request(function, *args, **kwargs):
    sleep_time = 60
    try:
        return function(*args, **kwargs)
    except APIException as e:
        if e.code == 429:
            print "Rate limit on %s, sleeping for %s seconds..." % (function, sleep_time)
            time.sleep(sleep_time)
            return function(*args, **kwargs)
        else:
            raise e

if __name__ == '__main__':
    main()


