from asyncio import base_events
import base64
import requests

def authorize():
    clientId = "8bb28bb2f4ae4ef99fd7a176223c8841"
    secret = "e03bb69eaa174220849e0665e17ce6e2"
    redirectUri = "http://localhost:8888/"
    
    # URLS
    AUTH_URL = 'https://accounts.spotify.com/authorize'
    TOKEN_URL = 'https://accounts.spotify.com/api/token'
    BASE_URL = 'https://api.spotify.com/v1/'


    # Make a request to the /authorize endpoint to get an authorization code
    auth_code = requests.get(AUTH_URL, {
        'client_id': clientId,
        'response_type': 'code',
        'redirect_uri': 'https://open.spotify.com/collection/playlists',
        'scope': 'playlist-modify-private',
    })
    print(auth_code)

    auth_header = base64.urlsafe_b64encode((clientId + ':' + secret).encode('ascii'))
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic %s' % auth_header.decode('ascii')
    }

    payload = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': 'https://open.spotify.com/collection/playlists',
        #'client_id': CLIENT_ID,
        #'client_secret': CLIENT_SECRET,
    }

    # Make a request to the /token endpoint to get an access token
    access_token_request = requests.post(url=TOKEN_URL, data=payload, headers=headers)

    # convert the response to JSON
    access_token_response_data = access_token_request.json()

    print(access_token_response_data)

    # save the access token
    access_token = access_token_response_data['access_token']