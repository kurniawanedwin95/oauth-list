import os
import pathlib
import requests

from flask import Flask, render_template, session, abort, redirect, request, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId

from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from pip._vendor import cachecontrol
import google.auth.transport.requests

app = Flask (__name__)
app.secret_key = "oauth-list_key"
client = MongoClient('localhost', 27017) #port 27017
db = client.flask_db
entries = db.entries

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
    all_entries = entries.find()
    return render_template('index.html', entries=all_entries)

@app.route('/login')
def login():
    authorization_url , state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    flow.fetch_token(authorization_response=request.url)

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
    # return id_info
    return render_template('callback.html', id_info=id_info)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/index')

@app.route('/protected_page')
@login_is_required
def protected_page():
    return "list page here <a href='/logout'><button>Logout</button></a>"

@app.route('/entry', methods=("GET", "POST"))
def entry():
    user_id = "xxx"
    if request.method == "POST":
        content = request.form["content"]
        entries.insert_one({'content': content, 'user_id': user_id})
        return redirect(url_for('entry'))
    myquery = {'user_id':user_id}
    queried_entries = entries.find(myquery)

    return render_template('entry.html', entries=queried_entries, user_id=user_id)

@app.route('/<id>/delete/', methods=("GET", "POST"))
def delete(id):
    entries.delete_one({"_id": ObjectId(id)})
    return redirect(url_for('entry'))

#next feature is to tie the entries to a user id

if __name__ == "__main__":
    app.run(debug=True)
