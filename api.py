#!/usr/bin/env python2.7
#coding=utf8

from flask import (
    Flask, request, json, redirect, session, url_for, abort, jsonify)
from flask.ext.cors import CORS
from connection import get_connection
from requests_oauthlib import OAuth2Session
from config import *
import time
import os
from datetime import datetime
import requests
import ast


os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


@app.route("/api/chat/<string:channel>")
def api_chat_channel(channel):
    start = request.args.get("startDate")
    end = request.args.get("endDate")
    con = get_connection()
    with con:
        if start is not None and end is not None:
            try:
                start_date = datetime.strptime(start, '%Y-%m-%d %H:%M:%S').replace(hour=0, minute=0, second=0)
                end_date = datetime.strptime(end, '%Y-%m-%d %H:%M:%S').replace(hour=23, minute=59, second=59)
                cur = con.cursor()
                cur.execute(
                    """SELECT time, message, username FROM messages
                        WHERE channel = %s AND (time BETWEEN %s AND %s)
                        ORDER BY time DESC""",
                    [channel, start_date, end_date])
                entries = cur.fetchall()
                messages = {
                    "messageCount": len(entries),
                    "messages": []
                    }
                for entry in range(len(entries)):
                    messages["messages"].append({
                        "time": entries[entry][0],
                        "message": unicode(entries[entry][1], errors='replace'),
                        "author": entries[entry][2]
                    })
                return json.jsonify(messages)
            except:
                messages = {
                    "messageCount": 0,
                    "messages": []
                    }
                return json.jsonify(messages)
        else:
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
                    "message": unicode(entries[entry][1], errors='replace'),
                    "author": entries[entry][2]
                })
            return json.jsonify(messages)
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



@app.route("/api/chat/<string:channel>/<string:username>")
def api_channel_chat_user(channel, username):
    start = request.args.get("startDate")
    end = request.args.get("endDate")
    con = get_connection()
    with con:
        if start is not None and end is not None:
            try:
                start_date = datetime.strptime(start, '%Y-%m-%d %H:%M:%S').replace(hour=0, minute=0, second=0)
                end_date = datetime.strptime(end, '%Y-%m-%d %H:%M:%S').replace(hour=23, minute=59, second=59)
                cur = con.cursor()
                cur.execute(
                    """SELECT time, message FROM messages
                        WHERE channel = %s AND (time BETWEEN %s AND %s)
                        ORDER BY time DESC""",
                    [channel, start_date, end_date])
                entries = cur.fetchall()
                messages = {
                    "messageCount": len(entries),
                    "messages": []
                    }
                for entry in range(len(entries)):
                    messages["messages"].append({
                        "time": entries[entry][0],
                        "message": unicode(entries[entry][1], errors='replace')
                    })
                return json.jsonify(messages)
            except:
                messages = {
                    "messageCount": 0,
                    "messages": []
                    }
                return json.jsonify(messages)
        else:
            cur = con.cursor()
            cur.execute(
                """SELECT time, message FROM messages
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
                    "message": unicode(entries[entry][1], errors='replace')
                })
            return json.jsonify(messages)
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
    con = get_connection()
    with con:
        cur = con.cursor()
        cur.execute(
            """SELECT donation_points, time_points, time_in_chat
                FROM users WHERE username = %s
            """,
            [username])
        entry = cur.fetchone()
        points = {
            "points": {}
        }
        if entry:
            points["points"]["donationPoints"] = entry[0]
            points["points"]["timePoints"] = entry[1]
            points["points"]["timeInChat"] = entry[2]
            points["points"]["totalPoints"] = entry[0] + entry[1]
        else:
            points["points"]["donationPoints"] = 0
            points["points"]["timePoints"] = 0
            points["points"]["timeInChat"] = 0
            points["points"]["totalPoints"] = 0
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
        return json.jsonify(points)


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
                "command": unicode(entries[entry][0], errors='replace'),
                "creator": entries[entry][1],
                "userLevel": entries[entry][2],
                "time": entries[entry][3],
                "response": unicode(entries[entry][4], errors='replace'),
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


@app.route("/api/items")
def api_items():
    con = get_connection()
    with con:
        cur = con.cursor()
        cur.execute(
            """SELECT id, name, value
                FROM items""")
        entries = cur.fetchall()
        items = {
            "items": []
            }
        for entry in range(len(entries)):
            items["items"].append({
                "itemId": entries[entry][0],
                "itemName": entries[entry][1],
                "itemValue": entries[entry][2]
            })
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
        return json.jsonify(items)


@app.route("/api/items/<string:username>")
def api_items_username(username):
    con = get_connection()
    with con:
        cur = con.cursor()
        cur.execute(
            """SELECT items.id, items.name, useritems.quantity
                FROM useritems
                INNER JOIN items ON items.id = useritems.item_id
                WHERE username = %s""", [username])
        entries = cur.fetchall()
        items = {
            "itemCount": len(entries),
            "items": []
            }
        for entry in range(len(entries)):
            items["items"].append({
                "itemId": entries[entry][0],
                "itemName": entries[entry][1],
                "itemQuantity": entries[entry][2]
            })
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
        return json.jsonify(items)


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
                "nickname": unicode(entries[entry][2], errors='replace'),
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
    app.run(debug=True, threaded=True, host='0.0.0.0', port=8080)
