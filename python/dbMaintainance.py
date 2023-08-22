#! /bin/python3
"""
    This module contains all of the functions needed to maintian the Database
"""

from sqlite3 import Error
from datetime import date,timedelta
from sqlite3 import Connnection, connect 


def _run_statement (connection:Connection,statement:str) -> None:
    try:
        connection.cursor().execute(statement)
    except Error as e:
        print(e)
        quit(1)

def _run_select_statement (connection:Connection, statement:str) -> tuple:
    try:
        return connection.cursor().execute(statement).fetchall()

    except Error as e:
        print(e)
        quit(1)
        
def insert_all (connection:Connnection, table:str, list_to_insert:list[tuple], columns:tupl[str]) -> None:
    statement  = f"INSERT INTO {table} ({",".join(columns)}) VALUES ({'?' * len(columns)});"
    try:
        connection.cursor().executemany(statement,list_to_insert)
        connection.commit()
    except Error as e:
        print(e)
        quit(1)

def insert_select (connection:Connnection, table:str, select_statement:str, columns:tuple[str]) -> None:
    statement = f"INSERT INTO {table} ({','.join(coluumns)}) \n {select_statement}"
    try:
        connection.cursor().execute(statement)
        connection.commit()
    except Error as e:
        print(e)
        quit(1)

def connect(db_file:str) -> Connection:
    """Create a connection to a SQLite database"""
    try:
        return connect(db_file)
    except Error as e:
        print(e)
        quit(1)

def drop_table (connection:Connection, table_name:str) -> None:
    statement = f"DROP TABLE IF EXISTS {table_name};"
    _run_statement(connection, statement)

def create_asset_table (connection:Connection, table_name:str = "discovered_assets", table_header:tuple[str]=("source", "datefound", "hostname","fqdn","ip","mac")) -> None:
    statement = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(table_header)});"
    _run_statement(connection,statement)

def migrate_to_historical_data (connection:Connection) -> None:
    create_asset_table(connection, "historical_data")
    statement = "SELECT * FROM discovered_assets"
    result = _run_select_statement(connection,statement)
    insert_assets(connection, result, "historical_data")
    drop_table(connection, "discovered_assets")
    create_asset_table(connection)
    
def cull_historical_data_table (connection:Connection,retention_days:int) -> None:
    target_date = (date.today() - timedelta(days=retention_days)).toordinal()
    statement = f"DELETE FROM historical_data WHERE date_found < {target_date}"
    _run_statement(connection,statement)

def create_report_table (connection:Connection) -> None:
    table_name = "reportable_data"
    headers = ("sources", "hostname","fqdn","ip","mac","in_inventory INTEGER")
    create_asset_table(connection, table_name, headers)

def sanatize(string:str) -> str:
    return string.lower().replace(" ", "").replace("-","").replace("'","").replace("\"","")

def update_report_item_single_item (connection:Connnection, field:str, value:tuple, row_id:int, table_name:str="reportable_data") -> None:
    statement = "\n".join(
        (
            f"UPDATE {table_name}",
            f"SET {field} = ?",
            "WHERE rowid = ?"
        )
    )
    _run_statement(connection, statement)
    connection.commit()

def fill_nulls (connection:Connection) -> None:
    def s_find_nulls_for(field:str) -> str:
        return "\n".join(
            (
                "SELECT row_id, hostname, fqdn, ip, mac",
                "FROM reportable_data",
                f"WHERE {field} IS NULL"
            )
        )    

    def s_find_matches (field:str, match_field_name:str, match_field_value:str):
        return "\n". join(
            (
                f"SELECT {field}",
                "FROM discovered_assets",
                f"WHERE {field} NOT NULL",
                f"AND {match_field_name} = {match_field_value}"
            )
        )
    for field in ["hostname","fqdn","ip","mac"]:
        statement = s_find_nulls_for(field)
        assets = _run_select_statement(connection, statement)
        for (rowid, hostname, fqdn, ip, mac) in assets:
            
            
        

    
def fill_sources (connection:Connnnection) -> None:
    pass

def fill_in_inventory (connection:Connnnection, primary_inventory:str) -> None:
    pass

def populate_report_table (connection:Connection, primary_inventory:str) -> None:
    columns = ("hostname", "fqdn", "ip", "mac")
    statement =  "\n".join(
        (
            "SELECT DISTINCT",
            ",".join(columns),
            "FROM discovered_assets",
            "WHERE hostname NOT NULL AND",
            "fqdn NOT NULL AND",
            "ip NOT NULL AND",
            "mac NOT NULL"
        )
    )
    table_name = "reportable_data"
    insert_select(connection, table_name, statement, columns)

    def field_select(field:str, table_name, columns) -> str:
        return "\n".join(
            (
                "SELECT DISTINCT",
                ",".join(columns),
                "FROM discovered_assets",
                f"WHERE {field} NOT NULL",
                f"AND {field} NOT IN {table_name}"
            )
        )

    hostnames = field_select("hostname",table_name,columns)
    fqdns = field_select("fqdn",table_name,columns)
    ips = field_select("ip",table_name,columns)
    macs = field_select("mac",table_name,columns)

    for statement in (hostnames,fqdns,ips,macs):
        insert_select(connection,table_name,statement,columns)
        fill_nulls(connection)
    fill_sources(connection)
    fill_in_inventory(connection,primary_inventory)