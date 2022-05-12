from asyncio import base_events
import base64
from crypt import methods
import threading
import requests
from flask import Flask, redirect, request
import os
import string    
import random
import json
import time

# variables
clientId = os.environ.get('ClientId')
secret = os.environ.get('Secret')
redirectUri = os.environ.get('redirectUri')

# generates random string for authorization
def randomStringGenerator(length):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))

class Song:
    def __init__(self, songId, song, trackNumber, artist, albumId, album):
        self.songId = songId
        self.song = song
        self.trackNumber = trackNumber
        self.artist = artist
        self.albumId = albumId
        self.album = album
    
class Album:
    def __init__(self, albumId, albumName, artist, songs) -> None:
        self.albumId = albumId
        self.albumName = albumName
        self.artist = artist
        self.songs = songs

app = Flask(__name__)

# Gets link to redirect the callback and get a token
@app.route("/login", methods=['GET'])
def login():
    state = randomStringGenerator(16)
    scope = 'user-read-recently-played'

    authorizeUrl = f"https://accounts.spotify.com/authorize?response_type=code&client_id={clientId}&scope={scope}&redirect_uri={redirectUri}&state={state}"
    return redirect(authorizeUrl)

# Gets the token for authorizing requests 
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
            os.environ['accessToken'] = response['access_token']
            return redirect('/getRecentlyPlayedTracks')

# Gets the latest 20 songs listened
@app.route("/getRecentlyPlayedTracks", methods=['GET'])
def getRecentlyPlayedTracks():
    if os.environ.get('accessToken') == None:
        return redirect('/login')
    else:
        accessToken = os.environ.get('accessToken')
        
        url = 'https://api.spotify.com/v1/me/player/recently-played'

        headers = {
            'Authorization': 'Bearer ' + str(accessToken)
        }

        recentPlayed = requests.get(url, headers=headers)

        if recentPlayed.ok:
            recentPlayedResponse = recentPlayed.json()
            tracks = {}
            for item in range(len(recentPlayedResponse['items'])):
                songId = recentPlayedResponse['items'][item]['track']['id']
                songName = recentPlayedResponse['items'][item]['track']['name']
                trackNumber = recentPlayedResponse['items'][item]['track']['track_number']
                artist = recentPlayedResponse['items'][item]['track']['album']['artists'][0]['name']
                album = recentPlayedResponse['items'][item]['track']['album']['name']
                albumId = recentPlayedResponse['items'][item]['track']['album']['id']

                # add class here
                song = Song(songId, songName, trackNumber, artist, albumId, album)

                tracks[item] = song.__dict__
            
            jsonReturned = json.dumps(tracks)
            return jsonReturned

# get the info of the album by id
@app.route("/getAlbum/<string:albumId>", methods=['GET'])
def getAlbum(albumId):
    if os.environ.get('accessToken') == None:
        return redirect('/login')
    else:
        accessToken = os.environ.get('accessToken')
        
        url = f'https://api.spotify.com/v1/albums/{albumId}/tracks'

        headers = {
            'Authorization': 'Bearer ' + str(accessToken)
        }

        albums = requests.get(url, headers=headers)

        if albums.ok:
            albumResponse = albums.json()
            jsonReturned = json.dumps(albumResponse)
            return json.loads(jsonReturned)

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

def init():
    try:
        results = getRecentlyPlayedTracks()
    except Exception as e:
        print(e)

    print (results)

init()