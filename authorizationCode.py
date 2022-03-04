from asyncio import base_events
import base64
import requests

def authorize():
    clientId = "<clientid>"
    secret = "<secret>"

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

print(authorize())