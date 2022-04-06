from asyncio import base_events
import base64
import requests
from flask import Flask, redirect, request
import os
import string    
import random
import json

# variables
clientId = os.environ.get('ClientId')
secret = os.environ.get('Secret')
redirectUri = os.environ.get('redirectUri')

# generates random string for authorization
def randomStringGenerator(length):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))

# test flask
app = Flask(__name__)

@app.route("/login", methods=['GET'])
def login():
    state = randomStringGenerator(16)
    scope = 'user-read-recently-played'

    return redirect(f"https://accounts.spotify.com/authorize?response_type=code&client_id={clientId}&scope={scope}&redirect_uri={redirectUri}&state={state}")

@app.route("/callback", methods=['GET'])
def authorize():

    code = request.args.get('code')
    state = request.args.get('state')
    
    if state:
        
        base64_clientIdSecret = encoding(clientId, secret)

        url = 'https://accounts.spotify.com/api/token'

        headers = {
            'Authorization': 'Basic ' + base64_clientIdSecret
        }

        form = {
            'code': code,
            'redirect_uri': redirectUri,
            'grant_type': 'authorization_code'
        }

        jsonResult = requests.post(url, data=form, json=True, headers=headers)

        if jsonResult.ok:
            response = jsonResult.json()
            accessToken = response['access_token']
            refreshToken = response['refresh_token']

            url = 'https://api.spotify.com/v1/me/player/recently-played'

            headers = {
                'Authorization': 'Bearer ' + str(accessToken)
            }

            recentPlayed = requests.get(url, headers=headers)

            if recentPlayed.ok:

                recentPlayedResponse = recentPlayed.json()
                songs = recentPlayedResponse['items']['track']
                return songs
                

@app.route("/refresh_token")
def refreshToken():
    refresh_token = request.args.get('refresh_token')
    base64_clientIdSecret = encoding(clientId, secret)
    url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': 'Basic ' + base64_clientIdSecret
    }
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }

    refreshTokenCall = requests.post(url, data=data, headers=headers)

    if refreshTokenCall.ok:
        response = refreshTokenCall.json()
        accessToken = response['access_token']

        return accessToken


def encoding(clientId, secret):
    clientIdSecret = clientId + ':' + secret
    clientIdSecret_bytes = clientIdSecret.encode('ascii')
    base64_bytes = base64.b64encode(clientIdSecret_bytes)
    base64_clientIdSecret = base64_bytes.decode('ascii')
    return base64_clientIdSecret