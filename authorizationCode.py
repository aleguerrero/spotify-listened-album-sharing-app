from asyncio import base_events
import base64
import requests
from flask import Flask
import os

# test flask
app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

def authorize():
    clientId = os.environ.get('ClientId')
    secret = os.environ.get('Secret')

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
        response = jsonResult.json()
        return response['access_token']

def testApi(authentication):
    url = 'https://api.spotify.com/v1/me/player/recently-played'

    headers = {
        'Authorization': 'Bearer ' + str(authentication),
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    jsonResult = requests.get(url, json=True, headers=headers)
    
    print(jsonResult.json())

testApi(authorize())