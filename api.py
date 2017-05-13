#!/usr/bin/env python2.7
#coding=utf8

from flask import (
    Flask, request, json, redirect, session, url_for, abort, jsonify)
from flask.ext.cors import CORS
from requests_oauthlib import OAuth2Session
from config import *
from lib.queries import API
import time
import os
from lib.connection import get_connection
from datetime import datetime
import requests
import ast


os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
app = Flask(__name__)
cors = CORS(app, resources={r"/lorenzotherobot/*": {"origins": "*"}})


@app.route("/lorenzotherobot/chat/<string:channel>")
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


@app.route("/lorenzotherobot/chat/<string:channel>/<string:username>")
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


@app.route("/lorenzotherobot/points/<string:username>")
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


@app.route("/lorenzotherobot/commands/<string:channel>")
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


@app.route("/lorenzotherobot/items")
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


@app.route("/lorenzotherobot/items/<string:username>")
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


@app.route("/lorenzotherobot/pokemon/<string:username>")
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


@app.route("/lorenzotherobot/chatters/<string:channel>")
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

# ################ OAUTH PORTION # TODO: MOVE TO ANOTHER FILE ############### #


@app.route("/lorenzotherobot/twitchalerts/authorize")
def demo():
    """Step 1: User Authorization.

    Redirect the user/resource owner to the OAuth provider (i.e. Github)
    using an URL with a few key OAuth parameters.
    """
    twitchalerts = OAuth2Session(
        client_id, scope=scope, redirect_uri=redirect_uri)
    authorization_url, state = twitchalerts.authorization_url(
        authorization_base_url)

    print "authorization_url: ", authorization_url, "state: ", state
    # State is used to prevent CSRF, keep this for later.
    session['oauth_state'] = state
    return redirect(authorization_url)


# Step 2: User authorization, this happens on the provider.

@app.route("/lorenzotherobot/twitchalerts/authorized", methods=["GET"])
def callback():
    """ Step 3: Retrieving an access token.

    The user has been redirected back from the provider to your registered
    callback URL. With this redirection comes an authorization code included
    in the redirect URL. We will use that to obtain an access token.
    """
    print request.args.get('code', '')
    code = request.args.get('code', '')
    twitchalerts = OAuth2Session(
        client_id, redirect_uri=redirect_uri)  # state=session['oauth_state']
    token = twitchalerts.fetch_token(
        token_url, client_secret=client_secret, code=code)
    print token
    params = {'access_token': token['access_token'], 'limit': 100}
    # Get a user's donations
    d = twitchalerts.get(
        'https://www.twitchalerts.com/lorenzotherobot/v1.0/donations', params=params)
    print d.content
    print d
    return str(token["access_token"])


if __name__ == "__main__":
    # This allows us to use a plain HTTP callback
    os.environ['DEBUG'] = "1"
    app.secret_key = os.urandom(24)
    app.run(threaded=True, host='127.0.0.1', port=8080)
