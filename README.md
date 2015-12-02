# lorenzotheapi

An example for how to integrate your MySQL-based chatbot onto a web frontend, based on the bot found at:
https://github.com/singlerider/lorenzotherobot

## Installation

Setting up a virtual environment (ideally), installing dependencies, and gaining
credentials.

### Virtual Environment

I would recommend running this in a virtual environment to keep your
dependencies in check. If you'd like to do that, run:

`sudo pip install virtualenv`

Followed by:

`virtualenv venv`

This will create an empty virtualenv in your project directory in a folder
called "venv." To enable it, run:

`source venv/bin/activate`

and your console window will be in that virtualenv state. To deactivate, run:

`deactivate`

### Dependencies

To install all dependencies locally (preferably inside your activated
virtualenv), run:

`pip install -r requirements.txt`

### Further Steps

Make a copy of the example config file:

`cp src/config/config_example.py src/config/config.py`

Go in the config.py file and modify the existing information to reflect your
current credentials setup for your database.

Then modify your twitchalerts app's info to reflect your registered app.
Make sure to bookmark the page for your twitchalerts app so you don't lose this
information. To register an app, go to:

http://twitchalerts.com/oauth/apps/register

And have their documentation open as a resource:

https://twitchalerts.readme.io/docs/getting-started

#### MySQL Installation

Depending on your distribution, starting the server will be different, on a mac, this is accomplished by doing

`brew install mysql`

`mysql.server start`

You should already have your ideal permissions set up for your bot's database if you've made it to the point where
you're ready to display the information on a frontend.

### Dependencies

To install all dependencies locally (preferably inside your activated
virtualenv), run:

`pip install -r requirements.txt`

## To Run

Run

`./api.py`

### Now

You can navigate to any route in the api file and get a RESTful JSON response.
