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
6. Setup conf.json with access token
7. Optional: setup conf.json with email settings
6. Search away!

## StubHubAPIs
* [InventorySearch - V2](https://developer.stubhub.com/store/site/pages/doc-viewer.jag?category=Search&api=InventorySearchAPIv2&endpoint=searchListing&version=v2)
* [EventSearch - V3](https://developer.stubhub.com/store/site/pages/doc-viewer.jag?category=Search&api=EventSearchAPIv3&endpoint=searchforeventsv3&version=v3)

## Resources
* [Fetch Access Token Guide](http://ozzieliu.com/2016/06/21/scraping-ticket-data-with-stubhub-api/)


