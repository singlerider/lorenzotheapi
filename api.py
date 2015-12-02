#!/usr/bin/env python2.7

from flask import (
    Flask, request, json, redirect, session, url_for, abort, jsonify)
from flask.ext.cors import CORS
from connection import get_connection
from requests_oauthlib import OAuth2Session
from config import *
import time
import os
import datetime
import requests
import ast

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


@app.route("/api/chat/<string:channel>")
def api_channel_chat(channel):
    con = get_connection()
    with con:
        cur = con.cursor()
        cur.execute(
            """SELECT time, message, username FROM messages
                WHERE channel = %s ORDER BY time DESC""",
            [channel])
        entries = cur.fetchall()
        messages = {
            "messageCount": len(entries),
            "messages": []
            }
        for entry in range(len(entries)):
            messages["messages"].append({
                "time": entries[entry][0],
                "message": entries[entry][1],
                "author": entries[entry][2]
            })
        """
        {
          "messageCount": 2,
          "messages": [
            {
              "message": "This is an example chat message response",
              "time": "Tue, 01 Dec 2015 09:08:46 GMT",
              "author": "exampleusername1"
            },
            {
              "message": "This is a subsequent message in descending order",
              "time": "Tue, 01 Dec 2015 09:07:55 GMT",
              "author": "exampleusername2"
            }
          ]
        }
        """
        return json.jsonify(messages)


@app.route("/api/chat/<string:channel>/<string:username>")
def api_channel_chat_user(channel, username):
    con = get_connection()
    with con:
        cur = con.cursor()
        cur.execute(
            """SELECT time, message FROM messages WHERE username = %s
            AND channel = %s ORDER BY time DESC""",
            [username, channel])
        entries = cur.fetchall()
        messages = {
            "messageCount": len(entries),
            "messages": []
            }
        for entry in range(len(entries)):
            messages["messages"].append({
                "time": entries[entry][0],
                "message": entries[entry][1]
            })
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
        return json.jsonify(messages)


@app.route("/api/commands/<string:channel>")
def api_channel_commands(channel):
    con = get_connection()
    with con:
        cur = con.cursor()
        cur.execute(
            """SELECT command, creator, user_level, time, response, times_used
            FROM custom_commands WHERE channel = %s""", [channel])
        entries = cur.fetchall()
        commands = {
            "commandCount": len(entries),
            "commands": []
            }
        for entry in range(len(entries)):
            commands["commands"].append({
                "command": entries[entry][0],
                "creator": entries[entry][1],
                "userLevel": entries[entry][2],
                "time": entries[entry][3],
                "response": entries[entry][4],
                "timesUsed": entries[entry][5]
            })
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
        return json.jsonify(commands)


@app.route("/api/pokemon/<string:username>")
def api_pokemon_username(username):
    con = get_connection()
    with con:
        cur = con.cursor()
        cur.execute(
            """SELECT position, level, nickname, pokemon_id, caught_by,
                for_trade, asking_trade, asking_level, for_sale, asking_price
                FROM userpokemon WHERE username = %s
                ORDER BY userpokemon.position""", [username])
        entries = cur.fetchall()
        party = {
            "partyCount": len(entries),
            "party": []
            }
        for entry in range(len(entries)):
            party["party"].append({
                "position": entries[entry][0],
                "level": entries[entry][1],
                "nickname": entries[entry][2],
                "pokemonId": entries[entry][3],
                "caughtBy": entries[entry][4],
                "trade": {
                    "forTrade": entries[entry][5],
                    "askingTrade": entries[entry][6],
                    "askingLevel": entries[entry][7]
                },
                "sale": {
                    "forSale": entries[entry][8],
                    "askingPrice": entries[entry][9]
                }
            })
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
        return json.jsonify(party)


@app.route("/api/chatters/<string:channel>")
def api_channel_chatters(channel):
    url = "https://tmi.twitch.tv/group/user/{0}/chatters".format(channel)
    resp = requests.get(url)
    data = ast.literal_eval(resp.content)
    print type(data)
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
    return json.jsonify(data)

# ################ OAUTH PORTION # TODO: MOVE TO ANOTHER FILE ############### #


@app.route("/twitchalerts/authorize")
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

@app.route("/twitchalerts/authorized", methods=["GET"])
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
        'https://www.twitchalerts.com/api/v1.0/donations', params=params)
    print d.content
    print d
    return str(token["access_token"])


if __name__ == "__main__":
    # This allows us to use a plain HTTP callback
    os.environ['DEBUG'] = "1"
    app.secret_key = os.urandom(24)
    app.run(host='0.0.0.0', port=8080)
