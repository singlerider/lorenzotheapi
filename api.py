#!/usr/bin/env python2.7
# coding=utf8

import ast
import os
from config import (client_id, client_secret, redirect_uri, twitch_client_id,
                    twitch_client_secret, twitch_redirect_uri, twitch_scopes)
import sqlite3 as lite
import requests
from flask import Flask, json, redirect, request, session
from flask.ext.cors import CORS
from lib.queries import API
from requests_oauthlib import OAuth2Session

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


@app.route("/api/chat/<string:channel>")
def api_chat_channel(channel):
    start = request.args.get("startDate")
    end = request.args.get("endDate")
    api = API()
    messages = api.chat_channel(channel, start, end)
    return messages
    """
    {
      "messageCount": 2,
      "messages": [
        {
          "message": "This is the most recent message response",
          "time": "Tue, 01 Dec 2015 09:08:46 GMT",
          "author": "exampleusername1"
        },
        {
          "message": "This is a previous message in descending order",
          "time": "Tue, 01 Dec 2015 09:07:55 GMT",
          "author": "exampleusername2"
        }
      ]
    }
    """


@app.route("/api/chat/<string:channel>/<string:username>")
def api_channel_chat_user(channel, username):
    start = request.args.get("startDate")
    end = request.args.get("endDate")
    api = API()
    messages = api.channel_chat_user(channel, username, start, end)
    return messages
    """
    {
      "messageCount": 2,
      "messages": [
        {
          "message": "This is an example chat message response",
          "time": "Tue, 01 Dec 2015 09:08:46 GMT"
        },
        {
          "message": "This is a subsequent message in descending order",
          "time": "Tue, 01 Dec 2015 09:07:55 GMT"
        }
      ]
    }
    """


@app.route("/api/points/<string:username>")
def api_points_user(username):
    api = API()
    points = api.points_user(username)
    return points
    """
    {
      "points": {
        "donationPoints": 17030,
        "timeInChat": 390,
        "timePoints": 78,
        "totalPoints": 17420
      }
    }
    """


@app.route("/api/commands/<string:channel>")
def api_channel_commands(channel):
    api = API()
    commands = api.channel_commands(channel)
    return commands
    """
    {
      "commandCount": 2,
      "commands": [
        {
          "command": "!testcommand1",
          "creator": "exampleusername1",
          "response": "Example string response for command",
          "time": "Tue, 01 Dec 2015 02:07:10 GMT",
          "timesUsed": 1,
          "userLevel": "reg"
        },
        {
          "command": "!testcommand2",
          "creator": "exampleusername2",
          "response": "Another example string response",
          "time": "Tue, 01 Dec 2015 02:05:06 GMT",
          "timesUsed": 2,
          "userLevel": "mod"
        }
      ]
    }
    """


@app.route("/api/items")
def api_items():
    api = API()
    items = api.items()
    return items
    """
    {
      "items": [
        {
          "itemId": 0,
          "itemName": "Nugget",
          "itemValue": 1000
        },
        {
          "itemId": 1,
          "itemName": "Fire Stone",
          "itemValue": 750
        }
      ]
    }
    """


@app.route("/api/items/<string:username>")
def api_items_username(username):
    api = API()
    items = api.items_username(username)
    return items
    """
    {
      "itemCount": 1,
      "items": [
        {
          "itemId": 2,
          "itemName": "Water Stone",
          "itemQuantity": 1
        }
      ]
    }
    """


@app.route("/api/pokemon/<string:username>")
def api_pokemon_username(username):
    api = API()
    party = api.pokemon_username(username)
    return party
    """
    {
      "party": [
        {
          "caughtBy": "singlerider",
          "level": 5,
          "nickname": "Scyther",
          "pokemonId": 123,
          "position": 1,
          "sale": {
            "askingPrice": null,
            "forSale": 0
          },
          "trade": {
            "askingLevel": null,
            "askingTrade": null,
            "forTrade": 0
          }
        },
        {
          "caughtBy": "singlerider",
          "level": 28,
          "nickname": "Jolteon",
          "pokemonId": 135,
          "position": 2,
          "sale": {
            "askingPrice": null,
            "forSale": 0
          },
          "trade": {
            "askingLevel": 5,
            "askingTrade": 64,
            "forTrade": 2
          }
        }
      ],
      "partyCount": 2
    }
    """


@app.route("/api/chatters/<string:channel>")
def api_channel_chatters(channel):
    url = "https://tmi.twitch.tv/group/user/{0}/chatters".format(channel)
    resp = requests.get(url)
    data = ast.literal_eval(resp.content)
    return json.jsonify(data)
    """
    {
      "_links": {},
      "chatter_count": 148,
      "chatters": {
        "admins": [],
        "global_mods": [],
        "moderators": [
          "moderatorname1",
          "moderatorname2"
        ],
        "staff": [],
        "viewers": [
          "1o1canadian",
          "agentjesse"
        ]
      }
    }
    """


@app.route("/api/quotes/<string:channel>")
def api_channel_quotes(channel):
    api = API()
    quotes = api.channel_quotes(channel)
    return quotes
    """
    {
      "quoteCount": 15,
      "quotes": [
        {
          "createdBy": "singlerider",
          "game": "H1Z1",
          "quote": "we were just talking about you and your awesome cable management skills",
          "quoteNumber": 1
        },
        {
          "createdBy": "joecow",
          "game": "H1Z1",
          "quote": "JoeCow is the best -Everyone ever 2016",
          "quoteNumber": 2
        }
    }
    """

# ################ OAUTH PORTION # TODO: MOVE TO ANOTHER FILE ############### #


@app.route("/twitchalerts/authorize")
def twitchalerts_authorize():
    """Step 1: User Authorization.

    Redirect the user/resource owner to the OAuth provider (i.e. Github)
    using an URL with a few key OAuth parameters.
    """
    authorization_base_url = 'https://www.twitchalerts.com/api/v1.0/authorize'
    scope = ["donations.read", "donations.create"]
    twitchalerts = OAuth2Session(
        client_id, scope=scope, redirect_uri=redirect_uri)
    authorization_url, state = twitchalerts.authorization_url(
        authorization_base_url)
    # State is used to prevent CSRF, keep this for later.
    session['oauth_state'] = state
    return redirect(authorization_url)


# Step 2: User authorization, this happens on the provider.

@app.route("/twitchalerts/authorized", methods=["GET", "POST"])
def twitchalerts_authorized():
    """ Step 3: Retrieving an access token.

    The user has been redirected back from the provider to your registered
    callback URL. With this redirection comes an authorization code included
    in the redirect URL. We will use that to obtain an access token.
    """
    token_url = 'https://www.twitchalerts.com/api/v1.0/token'
    code = request.args.get('code', '')
    twitchalerts = OAuth2Session(
        client_id, redirect_uri=redirect_uri)  # state=session['oauth_state']
    token = twitchalerts.fetch_token(
        token_url, client_secret=client_secret, code=code)
    params = {'access_token': token['access_token'], 'limit': 100}
    data = twitchalerts.get(
        'https://www.twitchalerts.com/api/v1.0/donations', params=params)
    return str(token["access_token"])


@app.route("/twitch/authorize")
def twitch_authorize():
    """Step 1: User Authorization.

    Redirect the user/resource owner to the OAuth provider (i.e. Github)
    using an URL with a few key OAuth parameters.
    """
    authorization_base_url = "https://api.twitch.tv/kraken/oauth2/authorize" + \
        "?response_type=code" + \
        "&client_id=" + twitch_client_id + \
        "&redirect_uri=" + twitch_redirect_uri
    scope = twitch_scopes
    twitch = OAuth2Session(
        client_id=twitch_client_id, scope=scope,
        redirect_uri=twitch_redirect_uri)
    authorization_url, state = twitch.authorization_url(authorization_base_url)
    # State is used to prevent CSRF, keep this for later.
    session['oauth_state'] = state
    return redirect(authorization_url)


@app.route("/twitch/authorized", methods=["GET", "POST"])
def twitch_authorized():
    """ Step 3: Retrieving an access token.

    The user has been redirected back from the provider to your registered
    callback URL. With this redirection comes an authorization code included
    in the redirect URL. We will use that to obtain an access token.
    """
    token_url = "https://api.twitch.tv/kraken/oauth2/token"
    code = request.args.get('code', '')
    twitch = OAuth2Session(
        client_id=twitch_client_id, scope=twitch_scopes,
        redirect_uri=twitch_redirect_uri)
    token = twitch.fetch_token(
        token_url, client_secret=twitch_client_secret, code=code)
    username_url = "https://api.twitch.tv/kraken?oauth_token=" + \
        token["access_token"]
    username_resp = requests.get(url=username_url)
    username = json.loads(username_resp.content)["token"]["user_name"]
    con = lite.connect("twitch.db", check_same_thread=False)
    with con:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS auth(
                id INTEGER PRIMARY KEY,
                channel TEXT UNIQUE, twitch_oauth TEXT,
                twitchalerts_oauth TEXT, streamtip_oauth TEXT);
        """)
        con.commit()
        cur.execute("""
            INSERT OR IGNORE INTO auth VALUES (NULL, ?, ?, NULL, NULL);
        """, [username, token["access_token"]])
        cur.execute("""
            UPDATE auth SET twitch_oauth = ? WHERE channel = ?;
        """, [token["access_token"], username])
    return str("It worked! Thanks, " + username)


if __name__ == "__main__":
    # This allows us to use a plain HTTP callback
    os.environ['DEBUG'] = "1"
    app.secret_key = os.urandom(24)
    app.run(threaded=True, host='0.0.0.0', port=8080)
