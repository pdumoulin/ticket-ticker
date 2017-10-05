
import os
import time
import datetime
import json
import argparse

from pprint import pformat

from api_client import StubHubAPIClient, APIException, Listing
from mail_client import EmailClient

def main():
    cwd = os.path.dirname(os.path.realpath(__file__)) 

    parser = argparse.ArgumentParser()
    parser.add_argument('-q', required=True, type=int, help='number of tickets to search for')
    parser.add_argument('-p', required=True, type=float, help='max price per ticket in dollars and cents')
    parser.add_argument('-l', required=False, type=int, default=None, help='limit number of events')
    parser.add_argument('-f', action='store_true', help='apply advanced filtering')
    parser.add_argument('--date', required=False, type=str, default='', help='date of game (YYYY-MM-DD)')
    parser.add_argument('--home', required=False, type=str, default='', help='home team name')
    parser.add_argument('--away', required=False, type=str, default='', help='away team name')
    parser.add_argument('--conf', required=False, type=str, default='%s/conf/conf.json' % cwd,  help='config file loc')
    parser.add_argument('--emails', required=False, type=str, default=None, help='email to send results to')
    args = parser.parse_args()

    # variable args
    quantity = args.q
    max_price = args.p
    home_team = args.home.lower()
    away_team = args.away.lower()
    event_limit = args.l
    advanced_filtering = args.f
    date = args.date
    config_filename = args.conf
    emails = args.emails.split(',') if args.emails is not None else []

    # output to log some info
    print datetime.datetime.now()
    print ''
    print pformat(args)
    print ''

    # process config file and setup clients
    with open(config_filename) as config_file:
        config = json.load(config_file)
        api_client = StubHubAPIClient(config['access_token'], config['endpoint'])
        email_client = None
        if len(emails) > 0:
            email_client = EmailClient(
                config['email']['history'],
                config['email']['sender'], 
                config['email']['password']
            )

    # static filtering args
    event_status = 'active'
    exclude = [
        Listing.OBSTRUCTED,
        Listing.PIGGY_BACK
    ]

    # get events based on home and away team name
    search = ("%s %s" % (home_team, away_team)).title()
    events = request(api_client.get_events, search)

    # filter out events by status
    events = filter(lambda e: e.status == event_status, events)
    events = filter(lambda e: 'preseason' not in e.name.lower(), events)

    # filter out optional params
    if home_team != '':
        events = filter(lambda e: home_team in e.act_primary, events)
    if away_team != '':
        events = filter(lambda e: away_team in e.act_secondary, events)
    if date != '':
        events = filter(lambda e: date in e.date, events)

    # limit results to minimize ticket fetch requests
    if event_limit is not None:
        events = events[0:event_limit]

    print "%s events found!" % len(events)
    print ""

    # go through events to find tickets
    for event in events:

        # format event url based on search terms
        event.set_url(quantity, exclude, max_price)

        # get tickets for the event
        listings = request(api_client.get_listings, event.token, quantity, max_price)

        # filter out tickets with bad properties (some might not work anymore as of 2017...)
        listings = filter(lambda t: len(list(set(exclude) & set(t.categories))) == 0, listings)

        # get picky with some custom settings
        if advanced_filtering:
            listings = advanced_filter(event, listings)

        # output the results
        print event.output()
        for listing in listings:
            print listing.output()

        # send some emails
        if email_client is not None:
            num_sent = email_client.send_event(emails, event, listings)
            print "Sent %s emails!" % num_sent

def advanced_filter(event, listings):
    results = []
    if event.venue.lower() == 'madison square garden':
        for listing in listings:
            try:
                row_num = int(listing.row)
                if '200 Level ' in listing.section and row_num > 16:
                    continue
                if '400 Level ' in listing.section  and row_num > 2:
                    continue
                results.append(listing)
            except ValueError:
                results.append(listing)
    return results

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


