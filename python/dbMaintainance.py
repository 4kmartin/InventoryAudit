#! /bin/python3
"""
    This module contains all of the functions needed to maintian the Database
"""

from sqlite3 import Error
from datetime import date,timedelta
import sqlite3


def _run_statement (connection:sqlite3.Connection,statement:str) -> None:
    try:
        connection.cursor().execute(statement)
    except Error as e:
        print(e)
        quit(1)

def _run_select_statement (connection:sqlite3.Connection, statement:str) -> tuple:
    try:
        return connection.cursur().execute(statement).fetchone()
    except Error as e:
        print(e)
        quit(1)

def connect(db_file:str) -> sqlite3.Connection:
    """Create a connection to a SQLite database"""
    try:
        return sqlite3.connect(db_file)
    except Error as e:
        print(e)
        quit(1)

def create_asset_table (connection:sqlite3.Connection) ->None:
    statement = "CREATE TABLE IF NOT EXISTS discovered_assets (source, datefound INTEGER, hostname, fqdn, ip, mac);"
    _run_statement(connection,statement)

def cull_asset_table (connection:sqlite3.Connection,retention_days:int) -> None:
    target_date = (date.today() - timedelta(days=retention_days)).toordinal()
    statement = f"DELETE FROM discovered_assets WHERE date_found < {target_date}"
    _run_statement(connection,statement)

def insert_assets(connection:sqlite3.Connection, assets:list[tuple]) -> None:
    map(lambda x: print(x), assets)
    connection.cursor().executemany("INSERT INTO discovered_assets (source, datefound, hostname, fqdn, ip, mac) VALUES(?, ?, ?, ?, ?, ?);", assets)
    connection.commit()