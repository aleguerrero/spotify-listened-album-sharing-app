from crypt import methods
from authorizationCode import login
from flask import Flask, redirect, request

app = Flask(__name__)

@app.route("/recentPlayedTracks/", methods=["GET"])
@login
def getRecentlyPlayedTracks():

url = 'https://api.spotify.com/v1/me/player/recently-played'

headers = {
    'Authorization': 'Bearer ' + str(accessToken)
}

recentPlayed = requests.get(url, headers=headers)

if recentPlayed.ok:
    recentPlayedResponse = recentPlayed.json()
    tracks = {}
    for track in range(len(recentPlayedResponse['items'])):
        tracks[track] = recentPlayedResponse['items'][track]['track']
    jsonReturned = json.dumps(tracks)
    return json.loads(jsonReturned)