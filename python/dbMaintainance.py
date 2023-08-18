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
        return connection.cursor().execute(statement).fetchall()

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

def drop_table (connection:sqlite3.Connection, table_name:str) -> None:
    statement = f"DROP TABLE IF EXISTS {table_name};"
    _run_statement(connection, statement)

def create_asset_table (connection:sqlite3.Connection, table_name:str = "discovered_assets", table_header:tuple[str]=("source", "datefound", "hostname","fqdn","ip","mac")) -> None:
    statement = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(table_header)});"
    _run_statement(connection,statement)

def migrate_to_historical_data (connection:sqlite3.Connection) -> None:
    create_asset_table(connection, "historical_data")
    statement = "SELECT * FROM discovered_assets"
    result = _run_select_statement(connection,statement)
    insert_assets(connection, result, "historical_data")
    drop_table(connection, "discovered_assets")
    create_asset_table(connection)
    
def cull_historical_data_table (connection:sqlite3.Connection,retention_days:int) -> None:
    target_date = (date.today() - timedelta(days=retention_days)).toordinal()
    statement = f"DELETE FROM historical_data WHERE date_found < {target_date}"
    _run_statement(connection,statement)

def create_report_table (connection:sqlite3.Connection) -> None:
    table_name = "reportable_data"
    headers = ("sources TEXT NOT NULL", "datefound INTEGER NOT NULL", "hostname","fqdn","ip","mac","in_inventory INTEGER")
    create_asset_table(connection, table_name, headers)

def sanatize(string:str) -> str:
    return string.lower().replace(" ", "").replace("-","").replace("'","").replace("\"","")