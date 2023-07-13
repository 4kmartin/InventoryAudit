#! /bin/python3
"""
    This module contains all of the functions needed to maintian the Database
"""

from sqlite3 import Error
import sqlite3
from datetime import date 

def connect(db_file:str) -> sqlite3.Connection:
    """Create a connection to a SQLite database"""
    try:
        return sqlite3.connect(db_file)
    except Error as e:
        print(e)
        quit(1)

def create_current_table(connection:sqlite3.Connection) -> None:
    table_statement = "CREATE TABLE IF NOT EXISTS current (\n\tid integer PRIMARY KEY,\n\thostname text NOT NULL,\n\tip_address text,\n\tmac_address text\n\tdata_sources text NOT NULL\n);"
    try:
        cursor = connection.cursor()
        cursor.execute(table_statement)
    except Error as e:
        print(e)
        quit(1)

def create_previous_table(connection:sqlite3.Connection) -> None:
    table_statement = "CREATE TABLE IF NOT EXISTS previous (\n\tid integer PRIMARY KEY,\n\thostname text NOT NULL,\n\tip_address text,\n\tmac_address text\n\tdata_sources text NOT NULL\n);"
    try:
        cursor = connection.cursor()
        cursor.execute(table_statement)
    except Error as e:
        print(e)
        quit(1)

def move_current_to_previous(connection:sqlite3.Connection) -> None:
    statement = "DROP TABLE previous;/n "