#!/usr/bin/env python

from flask import Flask, render_template, request, json
from connection import get_connection
app = Flask(__name__)


@app.route("/lorenzotherobot/")
def main():
    con = get_connection()
    username = request.args.get("username")
    print username
    with con:
        cur = con.cursor()
        cur.execute(
            "SELECT time, message FROM messages WHERE username = %s",
            [username])
        entries = cur.fetchall()
        entries = [[x[0], x[1]] for x in entries]
        messages = {"messages": entries}
        # return json.jsonify(messages)
        return render_template('index.html')


@app.route('/showsignup')
def showsignup():
    con = get_connection()
    return render_template('signup.html')

if __name__ == "__main__":
    app.run(debug=True)
