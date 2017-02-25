
# https://developer.stubhub.com/store/site/pages/doc-tutorials.jag

import base64
import requests

app_token = raw_input('Enter app token: ')
consumer_key = raw_input('Enter consumer key: ')
consumer_secret = raw_input('Enter consumer secret: ')

username = raw_input('Enter username: ')
password = raw_input('Enter password: ')

auth = 'Basic ' + base64.b64encode(consumer_key + ":" + consumer_secret)

response = requests.post(
    'https://api.stubhub.com/login',
    headers={
        'Content-Type'  : 'application/x-www-form-urlencoded',
        'Authorization' : auth
    },
    data={
        'grant_type' : 'password',
        'username'   : username,
        'password'   : password
    }
)

# TODO - refresh token syntax
# grant_type=refresh_token&refresh_token=yourRefreshToke

response_body = response.json()
print response_body['access_token']
print response_body['refresh_token']
print response.headers['X-StubHub-User-GUID']

