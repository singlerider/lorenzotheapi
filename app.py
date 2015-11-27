#!/usr/bin/env python2.7

from flask import Flask, render_template, request, json
from flask.ext.cors import CORS
from connection import get_connection
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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
