from flask import json
from lib.connection import get_connection


class API:

    def __init__(self):
        self.con = get_connection()

    def chat_channel(self, channel, start, end):
        with self.con:
            if start is not None and end is not None:
                try:
                    start_date = datetime.strptime(
                        start, '%Y-%m-%d %H:%M:%S').replace(
                            hour=0, minute=0, second=0)
                    end_date = datetime.strptime(
                        end, '%Y-%m-%d %H:%M:%S').replace(
                            hour=23, minute=59, second=59)
                    cur = self.con.cursor()
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
                            "message": unicode(
                                entries[entry][1], errors='replace'),
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
                cur = self.con.cursor()
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
                        "message": unicode(
                            entries[entry][1], errors='replace'),
                        "author": entries[entry][2]
                    })
                return json.jsonify(messages)

    def channel_chat_user(self, channel, username, start, end):
        with self.con:
            if start is not None and end is not None:
                try:
                    start_date = datetime.strptime(
                        start, '%Y-%m-%d %H:%M:%S').replace(
                            hour=0, minute=0, second=0)
                    end_date = datetime.strptime(
                        end, '%Y-%m-%d %H:%M:%S').replace(
                            hour=23, minute=59, second=59)
                    cur = self.con.cursor()
                    cur.execute(
                        """SELECT time, message FROM messages
                            WHERE channel = %s AND username = %s
                            AND (time BETWEEN %s AND %s)
                            ORDER BY time DESC""",
                        [channel, username, start_date, end_date])
                    entries = cur.fetchall()
                    messages = {
                        "messageCount": len(entries),
                        "messages": []
                        }
                    for entry in range(len(entries)):
                        messages["messages"].append({
                            "time": entries[entry][0],
                            "message": unicode(
                                entries[entry][1], errors='replace')
                        })
                    return json.jsonify(messages)
                except:
                    messages = {
                        "messageCount": 0,
                        "messages": []
                        }
                    return json.jsonify(messages)
            else:
                cur = self.con.cursor()
                cur.execute(
                    """SELECT time, message FROM messages
                        WHERE channel = %s AND username = %s
                        ORDER BY time DESC""",
                    [channel, username])
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

    def points_user(self, username):
        with self.con:
            cur = self.con.cursor()
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
            return json.jsonify(points)

    def channel_commands(self, channel):
        with self.con:
            cur = self.con.cursor()
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
            return json.jsonify(commands)

    def items(self):
        with self.con:
            cur = self.con.cursor()
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
            return json.jsonify(items)

    def items_username(self, username):
        with self.con:
            cur = self.con.cursor()
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
            return json.jsonify(items)

    def pokemon_username(self, username):
        with self.con:
            cur = self.con.cursor()
            cur.execute(
                """SELECT position, level, nickname, pokemon_id, caught_by,
                    for_trade, asking_trade, asking_level, for_sale,
                    asking_price FROM userpokemon WHERE username = %s
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
            return json.jsonify(party)
