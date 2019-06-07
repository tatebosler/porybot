import sqlite3
from sqlite3 import Error

def connect(path):
    try:
        connection = sqlite3.connect(path)
        return connection
    except Error as e:
        print e
        return None
