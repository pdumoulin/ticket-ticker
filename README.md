# ticket-ticker

StubHubAPI Sports Search

## Configuration Structure
```json
{
    "endpoint"        : "https://api.stubhub.com/",
    "access_token"    : "",
    "email"           : {
        "sender"   : "",
        "password" : "",
        "history"  : ""
    }
}

```

## Search Usage
```bash
usage: search.py [-h] -q Q -p P [-l L] [--date DATE] [--home HOME]
                 [--away AWAY] [--conf CONF] [--emails EMAILS]

optional arguments:
  -h, --help       show this help message and exit
  -q Q             number of tickets to search for
  -p P             max price per ticket in dollars and cents
  -l L             limit number of events
  --date DATE      date of game (YYYY-MM-DD)
  --home HOME      home team name
  --away AWAY      away team name
  --conf CONF      config file loc
  --emails EMAILS  email to send results to

```

## Setup
1. Create StubHub account [here](https://myaccount.stubhub.com/login/register)
2. Create new application [here](https://developer.stubhub.com/store/site/pages/applications.jag)
3. Subscribe to all APIs [here](https://developer.stubhub.com/store/apis/info)
4. Email apisupport@stubhub.com to request InventorySearch V2 API access
5. Create access token using scripts/get_access_token.py
6. Setup conf file with access token
6. Search away!

## Email Setup
1. Add email credentials to conf file
2. Create email history pickle
3. Add pickle file location to conf file

```bash
touch email_history.p
Python 2.7.9 (default, Mar  8 2015, 00:52:26)
[GCC 4.9.2] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import pickle
>>> pickle.dump({}, open('email_history.p', 'wb'))
```

## StubHubAPIs
* [InventorySearch - V2](https://developer.stubhub.com/store/site/pages/doc-viewer.jag?category=Search&api=InventorySearchAPIv2&endpoint=searchListing&version=v2)
* [EventSearch - V3](https://developer.stubhub.com/store/site/pages/doc-viewer.jag?category=Search&api=EventSearchAPIv3&endpoint=searchforeventsv3&version=v3)

## Resources
* [Fetch Access Token Guide](http://ozzieliu.com/2016/06/21/scraping-ticket-data-with-stubhub-api/)


