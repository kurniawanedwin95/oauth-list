import os
import pathlib
import requests

from flask import render_template, session, abort, redirect, request
from app import app

from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from pip._vendor import cachecontrol
import google.auth.transport.requests
app.secret_key = "oauth-list_key"

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = '178865085250-deeo0oedoa45n4k32k7l4moe5athuq98.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = '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'
REDIRECT_URI = 'http://127.0.0.1:5000/callback'

client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")
flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes = ["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri = "http://127.0.0.1:5000/callback" )
# google_auth_oauthlib's Flow is a class that uses requests_oauthlib.OAuth2Session to perform the OAuth2 logic


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            abort(401) #authorization login_is_required
        else:
            return function()
    return wrapper

@app.route('/')
@app.route('/index')
def main():
    return render_template('index.html')

@app.route('/login')
def login():
    authorization_url , state = flow.authorization_url()
    session["state"] = state

    return redirect(authorization_url)

@app.route('/callback')
def callback():
    flow.fetch_token(authorization_response=request.url)

    test1 = session["state"]
    test2 = request.args["state"]

    print (f"this is session state {test1}")
    print (f"this is request args state {test2}")

    if not session["state"] == request.args["state"]:
        abort(500) #state does not match and prevent cross state attacks

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)
    id_info = id_token.verify_oauth2_token(
        id_token = credentials._id_token,
        request = token_request,
        audience = GOOGLE_CLIENT_ID
    )
    return id_info
    # return render_template('callback.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/index')

@app.route('/protected_page')
@login_is_required
def protected_page():
    return "list page here <a href='/logout'><button>Logout</button></a>"


if __name__ == "__main__":
    app.run(debug=True)
