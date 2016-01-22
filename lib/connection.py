import sys
from config import mysql_credentials

import MySQLdb as mdb


def get_connection():
    login = mysql_credentials
    con = mdb.connect(login[0], login[1], login[2], login[3])
    return con
