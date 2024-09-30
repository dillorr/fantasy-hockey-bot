from yahoo_oauth import OAuth2


# authenticates with yahoo oauth, and refreshes token if necessary
def authenticate_yahoo() -> OAuth2:
    oauth = OAuth2(
        consumer_secret=None, consumer_key=None, from_file=".config/oauth2.json"
    )

    if not oauth.token_is_valid():
        oauth.refresh_access_token()

    return oauth
