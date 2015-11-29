#!/usr/bin/env python2.7

from flask import Flask, render_template, request, json, redirect, session, url_for
from flask.ext.cors import CORS
from connection import get_connection
from requests_oauthlib import OAuth2Session
from flask.json import jsonify
from config import *
import os

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


@app.route("/curvyllama")
def main():
    return render_template('index.html')

@app.route("/api/curvyllama")
def api():
    con = get_connection()
    username = request.args.get("username")
    print username
    with con:
        cur = con.cursor()
        cur.execute(
            "SELECT time, message FROM messages WHERE username = %s ORDER BY time DESC",
            [username])
        entries = cur.fetchall()
        entries = [[x[0], x[1]] for x in entries]
        messages = {"messages": entries}
        return json.jsonify(messages)

@app.route('/showsignup')
def showsignup():
    con = get_connection()
    return render_template('signup.html')


# This information is obtained upon registration of a new GitHub OAuth
# application here: https://github.com/settings/applications/new


authorization_base_url = 'https://www.twitchalerts.com/api/v1.0/authorize'
token_url = 'https://www.twitchalerts.com/api/v1.0/token'
scope = ["donations.read", "donations.create"]


@app.route("/authorize")
def demo():
    """Step 1: User Authorization.

    Redirect the user/resource owner to the OAuth provider (i.e. Github)
    using an URL with a few key OAuth parameters.
    """
    twitchalerts = OAuth2Session(client_id, scope=scope, redirect_uri=redirect_uri)
    authorization_url, state = twitchalerts.authorization_url(authorization_base_url)

    print "authorization_url: ", authorization_url, "state: ", state
    # State is used to prevent CSRF, keep this for later.
    session['oauth_state'] = state
    return redirect(authorization_url)


# Step 2: User authorization, this happens on the provider.

@app.route("/authorized", methods=["GET"])
def callback():
    """ Step 3: Retrieving an access token.

    The user has been redirected back from the provider to your registered
    callback URL. With this redirection comes an authorization code included
    in the redirect URL. We will use that to obtain an access token.
    """
    print request.args.get('code', '')
    code = request.args.get('code', '')
    twitchalerts = OAuth2Session(client_id, redirect_uri=redirect_uri) #state=session['oauth_state']
    token = twitchalerts.fetch_token(token_url, client_secret=client_secret, code=code)
    print token
    params = {'access_token': token['access_token'], 'limit':100 }
    # Get a user's donations
    d = twitchalerts.get('https://www.twitchalerts.com/api/v1.0/donations', params=params)
    print d.content
    print d
    return str(token["access_token"])


if __name__ == "__main__":
    # This allows us to use a plain HTTP callback
    os.environ['DEBUG'] = "1"

    app.secret_key = os.urandom(24)
    app.run(host='0.0.0.0', port=8080)
