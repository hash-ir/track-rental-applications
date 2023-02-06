import yaml
from flask import Flask, make_response, redirect, url_for, request
from requests_oauthlib import OAuth1Session


# Load config
with open('config.yml') as f:
    config = yaml.load(f, yaml.FullLoader)
    CLIENT_KEY = config['client_key']
    CLIENT_SECRET = config['client_secret']

    oauth_token, oauth_token_secret, oauth_verifier = None, None, None
    request_token_url = config['base_url'] + config['request_token_uri']
    authorization_url = config['base_url'] + config['user_auth_uri']
    access_token_url = config['base_url'] + config['access_token_uri']


app = Flask(__name__)


@app.route('/')
def index():
    """Home page."""
    return 'Hello World'


@app.route('/initialize') # type: ignore
def init():
    """Initialize authorization process."""

    # Create an OAuth1Session object for getting a request token
    oauth1 = OAuth1Session(
        client_key=CLIENT_KEY, \
        client_secret=CLIENT_SECRET,
        callback_uri='http://127.0.0.1:5000/callback' # catch the callback
    )

    # Get a request token from the API
    fetch_response = oauth1.fetch_request_token(request_token_url)
    oauth_token = fetch_response.get('oauth_token')
    oauth_token_secret = fetch_response.get('oauth_token_secret')

    # Redirect the user to the authorization page
    auth_url = oauth1.authorization_url(authorization_url)
    print('Redirecting to', auth_url)
    return redirect(auth_url)


@app.route('/callback') # type: ignore
def authorize():
    """Authorize the app to access the user's data."""

    # Read the state parameter from the callback URL
    if request.args.get('state') == 'authorized':
        oauth_verifier = request.args.get('oauth_verifier')

        # Create an OAuth1Session object for getting an access token
        oauth1 = OAuth1Session(
            client_key=CLIENT_KEY,
            client_secret=CLIENT_SECRET,
            resource_owner_key=oauth_token,
            resource_owner_secret=oauth_token_secret,
            verifier=oauth_verifier
        )

        # Get an access token from the API
        fetch_response = oauth1.fetch_access_token(access_token_url)
        access_token = fetch_response.get('oauth_token')

        # Save the access token to the config file
        with open('config.yml', 'a') as f:
            config = yaml.load(f, yaml.FullLoader)
            config['access_token'] = access_token

        return 'Authorized'

    else: # state = 'rejected'
        return 'Not authorized'
    