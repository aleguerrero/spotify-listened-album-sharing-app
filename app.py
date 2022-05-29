from asyncio import base_events
import base64
from crypt import methods
import threading
import requests
from flask import Flask, redirect, request, jsonify
import os
import string    
import random
import json
import time

# variables
clientId = os.environ.get('ClientId')
secret = os.environ.get('Secret')
redirectUri = os.environ.get('redirectUri')

# Get Album
album = None

# generates random string for authorization
def randomStringGenerator(length):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))

class Song:
    def __init__(self, songId, song, trackNumber, artist, albumId, album, listened):
        self.songId = songId
        self.song = song
        self.trackNumber = trackNumber
        self.artist = artist
        self.albumId = albumId
        self.album = album
        self.listened = listened
    
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
            grptThread.start()
            return 'Got Access Token!' 

# Gets the latest 20 songs listened
@app.route("/getRecentlyPlayedTracks", methods=['GET'])
def getRecentlyPlayedTracks():
    if os.environ.get('accessToken') == None:
        return redirect('/login')
    else:
        while True:
            accessToken = os.environ.get('accessToken')
            
            url = 'https://api.spotify.com/v1/me/player/recently-played'

            headers = {
                'Authorization': 'Bearer ' + str(accessToken)
            }

            recentPlayed = requests.get(url, headers=headers)

            if recentPlayed.ok:
                recentPlayedResponse = recentPlayed.json()

                # songId = recentPlayedResponse['items'][0]['track']['id']
                # songName = recentPlayedResponse['items'][0]['track']['name']
                trackNumber = recentPlayedResponse['items'][0]['track']['track_number']
                # artist = recentPlayedResponse['items'][0]['track']['album']['artists'][0]['name']
                # albumSong = recentPlayedResponse['items'][0]['track']['album']['name']
                albumId = recentPlayedResponse['items'][0]['track']['album']['id']

                # add class here
                # song = Song(songId, songName, trackNumber, artist, albumId, albumSong, True)
                
                # print(song.__dict__)

                global album

                if trackNumber == 1:
                    if album == None or album.albumId != albumId:
                        album = getAlbum(albumId)
                    
                elif album != None and album.albumId == albumId:
                    if album.songs[trackNumber].listened == False:
                        album.songs[trackNumber].listened = True                 

            time.sleep(10)

# get the info of the album by id
@app.route("/getAlbum/<string:albumId>", methods=['GET'])
def getAlbum(albumId):
    if os.environ.get('accessToken') == None:
        return redirect('/login')
    else:
        accessToken = os.environ.get('accessToken')
        
        url = f'https://api.spotify.com/v1/albums/{albumId}'

        headers = {
            'Authorization': 'Bearer ' + str(accessToken)
        }

        albumTracks = requests.get(url, headers=headers)

        if albumTracks.ok:
            albumResponse = albumTracks.json()
            
            # creates album
            albumToCreate = Album(
                albumId=albumResponse['id'],
                albumName=albumResponse['name'],
                artist=albumResponse['artists'][0]['name'],
                songs=None
            )

            # creates songs array and adds them
            songsArray = {}
            for track in albumResponse['tracks']['items']:
                songsArray[track['track_number']] = Song(
                    songId=track['id'],
                    song=track['name'],
                    trackNumber=track['track_number'],
                    artist=track['artists'][0]['name'],
                    albumId=albumToCreate.albumId,
                    album=albumToCreate.albumName,
                    listened=False
                )

            songsArray[1].listened=True

            albumToCreate.songs=songsArray

            return albumToCreate

@app.route("/getAlbumProgress")
def getAlbumProgress():
    global album
    if album != None:
        albumDict = album.__dict__
        songsDict = []
        for i, (trackNumber, song) in enumerate(album.songs.items()):
            songsDict[trackNumber] = song.__dict__
        albumDict['songs'] = songsDict
        return jsonify(albumDict)
    
    return 'No album yet'

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

grptThread = threading.Timer(10, getRecentlyPlayedTracks)