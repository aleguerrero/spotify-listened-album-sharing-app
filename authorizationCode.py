from asyncio import base_events
import base64
import requests

def authorize():
    clientId = "8bb28bb2f4ae4ef99fd7a176223c8841"
    secret = "e03bb69eaa174220849e0665e17ce6e2"

    clientIdSecret = clientId + ':' + secret
    clientIdSecret_bytes = clientIdSecret.encode('ascii')
    base64_bytes = base64.b64encode(clientIdSecret_bytes)
    base64_clientIdSecret = base64_bytes.decode('ascii')

    url = 'https://accounts.spotify.com/api/token'

    headers = {
        'Authorization': 'Basic ' + base64_clientIdSecret
    }

    form = {
        'grant_type': 'client_credentials'
    }

    jsonResult = requests.post(url, data=form, json=True, headers=headers)

    if jsonResult.ok:
        print (jsonResult.json())

def testApi(authentication):
    url = 'https://api.spotify.com/v1/me/player/recently-played'

    headers = {
        'Authorization': 'Bearer ' + authentication
    }

    form = {
        'grant_type': 'client_credentials'
    }

    jsonResult = requests.post(url, data=form, json=True, headers=headers)

print(authorize())