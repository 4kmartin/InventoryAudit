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

def drop_table (connection:sqlite3.Connection, table_name:str):
    statement = f"DROP TABLE IF EXISTS {table_name};"
    _run_statement(connection, statement)

def create_asset_table (connection:sqlite3.Connection, table_name:str = "discovered_assets", table_header:tuple[str]=("source", "datefound", "hostname","fqdn","ip","mac")) ->None:
    statement = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(table_header)});"
    _run_statement(connection,statement)

def cull_asset_table (connection:sqlite3.Connection,retention_days:int) -> None:
    target_date = (date.today() - timedelta(days=retention_days)).toordinal()
    statement = f"DELETE FROM discovered_assets WHERE date_found < {target_date}"
    _run_statement(connection,statement)

def insert_assets(connection:sqlite3.Connection, assets:list[tuple], table_name:str="discovered_assets", table_header:tuple[str]=("source","datefound","hostname","fqdn","ip","mac")) -> None:
    # map(lambda x: print(x), assets)
    connection.cursor().executemany(f"INSERT INTO {table_name} ({', '.join(table_header)}) VALUES(?, ?, ?, ?, ?, ?);", assets)
    connection.commit()

def collate_data (connection:sqlite3.Connection, source_to_exclude:str = ""):
    """Colates all the duplicate data into single assets on a seperate table, optionally you can ignore data provided by a specific source"""
    table_name = "collated_assets"
    table_header = ("name", "fqdn", "ip", "mac")
    statement = "\n".join(("SELECT DISTINCT",
        "ifnull(a.hostname, b.hostname) as name,",
        "ifnull(a.fqdn, b.fqdn) as fqdn,",
        "ifnull(a.ip, b.ip) as ip,",
        "ifnull(a.mac, b.mac) as mac",
        f"FROM (SELECT * FROM discovered_assets WHERE source != '{source_to_exclude}') a",
        f"INNER JOIN (SELECT * FROM discovered_assets WHERE source != '{source_to_exclude}') b on a.mac = b.mac;"
    ))
    drop_table(connection, table_name)
    create_asset_table(connection, table_name, table_header)
    insert_assets(connection, _run_select_statement(connection,statement),table_name,table_header)
    matching_name = "\n".join(
        (
            "SELECT DISTINCT",
            "ifnull(a.hostname, b.hostname) as name,",
            "ifnull(a.fqdn, b.fqdn) as fqdn,",
            "ifnull(a.ip,b.ip) as ip,",
            "ifnull(a.mac, b.mac) as mac",
            f"FROM (SELECT * FROM discovered_assets WHERE source != '{source_to_exclude}') a",
            f"INNER JOIN (SELECT * FROM discovered_assets WHERE source != '{source_to_exclude}') b on a.hostname = b.hostname;"
        )
    )
    statement = "\n".join(
        (
            "SELECT *",
            f"FROM (\n{matching_name})",
            f"WHERE name NOT IN (SELECT name FROM {table_name});"
        )
    )
    insert_assets(connection,_run_select_statement(connection,statement),table_name,table_header)
    
def collate_from_source(connection:sqlite3.Connection, source:str):
    table_name = f"collated_from_{source.replace(' ', '_')}"
    table_header = ("name","fqdn","ip","mac")
    drop_table(connection, table_name)
    create_asset_table(connection, table_name, table_header)
    statement = "\n".join((
        f"INSERT INTO {table_name}",
        "SELECT DISTINCT",
        "ifnull(a.hostname, b.hostname) as name,",
        "ifnull(a.fqdn, b.fqdn) as fqdn,",
        "ifnull(a.ip,b.ip) as ip,",
        "ifnull(a.mac,b.mac) as mac",
        f"FROM (SELECT * FROM discovered_assets WHERE source = '{source}') a",
        f"LEFT OUTER JOIN (SELECT * FROM discovered_assets WHERE source != '{source}') b ON a.hostname = b.hostname;"
    ))
    _run_statement(connection, statement)