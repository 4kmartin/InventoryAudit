#! /bin/python3
"""
    This module contains all of the functions needed to maintian the Database
"""

from sqlite3 import Error
from datetime import date,timedelta
from sqlite3 import Connection, connect 
from typing import Callable, Any


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
        
def insert_all (connection:Connection, table:str, list_to_insert:list[tuple], columns:tuple[str]) -> None:
    statement  = f"INSERT INTO {table} ({','.join(columns)}) VALUES (?{', ?' * (len(columns)-1)});"
    try:
        connection.cursor().executemany(statement,list_to_insert)
        connection.commit()
    except Error as e:
        print(e)
        quit(1)

def insert_select (connection:Connection, table:str, select_statement:str, columns:tuple[str]) -> None:
    statement = f"INSERT INTO {table} ({','.join(columns)}) \n {select_statement}"
    try:
        connection.cursor().execute(statement)
        connection.commit()
    except Error as e:
        print(e)
        quit(1)

def get_db_connection(db_file:str) -> Connection:
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
    headers = ("source", "hostname","fqdn","ip","mac","in_inventory INTEGER")
    create_asset_table(connection, table_name, headers)

def sanatize(string:str) -> str:
    return string.lower().replace(" ", "").replace("-","").replace("'","").replace("\"","")

def update_report_item_single_item (connection:Connection, field:str, value:tuple, rowid:int, table_name:str="reportable_data") -> None:
    statement = "\n".join(
        (
            f"UPDATE {table_name}",
            f"SET {field} = ?",
            "WHERE rowid = ?"
        )
    )
    connection.cursor().execute(statement,(value,rowid))
    connection.commit()

def s_find_nulls_for(field:str) -> str:
    return "\n".join(
        (
            "SELECT rowid, hostname, fqdn, ip, mac",
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
            f"AND {match_field_name} = '{match_field_value}'"
        )
    )

def field_select(field:str, table_name, columns) -> str:
    return "\n".join(
        (
            "SELECT DISTINCT",
            ",".join(columns),
            "FROM discovered_assets",
            f"WHERE {field} NOT NULL",
            f"AND {field} NOT IN (SELECT hostname FROM {table_name})"
        )
    )

def s_completed_rows (columns:tuple[str]) -> str:
    return "\n".join(
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

def iterate_list_of_assets_with_null_field (connection:Connection, function_to_call:Callable[[Connection,tuple[Any],str], None], asset_list:list[tuple[Any]], null_field:str) -> None:
    for asset in asset_list:
        function_to_call(connection, asset, null_field)

def lookup_matching_values_then_update_null_fields (connection:Connection, asset:tuple[int, str, str, str, str], null_field:str) -> None:
    (rowid, lookup) = map_lookup_to_values(asset)
    for (key, value) in lookup.items():
        if not value:
            continue
        statement = s_find_matches(null_field, key, value)
        matched_asset = connection.cursor().execute(statement).fetchone()
        if matched_asset:
            update_report_item_single_item(connection,null_field,matched_asset[0],rowid)
            break

def append_data_to_field (connection:Connection, asset:tuple[Any], field:str, table_name:str = "reportable_data") -> None:
    (rowid, lookup) = map_lookup_to_values(asset)
    getter = f"SELECT {field} FROM {table_name} WHERE rowid = {rowid};"
    current_value = _run_select_statement(connection,getter)[0][0]
    field_value = [current_value] if current_value else []
    for (key, value) in lookup.items():
        statement = s_find_matches(field, key, value)
        matched_assets = connection.cursor().execute(statement).fetchall()
        if not matched_assets:
            continue
        for matched_asset in matched_assets:
            if matched_asset[0] and matched_asset[0] not in field_value:
                field_value.append(matched_asset[0])
    print(field_value)
    update_report_item_single_item (connection, field, ",".join(field_value), rowid)
        

def map_lookup_to_values (asset:tuple[int,str,str,str,str]) -> tuple[int,dict[str,Any]]:
    return (asset[0],
        {
            "hostname":asset[1],
            "fqdn":asset[2],
            "ip":asset[3],
            "mac":asset[4]
        }
    )

def fill_nulls (connection:Connection) -> None:    
    for field in ["hostname","fqdn","ip","mac"]:
        statement = s_find_nulls_for(field)
        assets = _run_select_statement(connection, statement)
        iterate_list_of_assets_with_null_field(connection, lookup_matching_values_then_update_null_fields,assets,field)

def fill_source (connection:Connection) -> None:
    statement = "SELECT rowid, hostname, fqdn, ip, mac FROM reportable_data"
    assets = _run_select_statement(connection, statement)
    iterate_list_of_assets_with_null_field(connection, append_data_to_field, assets, "source")

def fill_in_inventory (connection:Connection, primary_inventory:str) -> None:
    collected_scources = _run_select_statement(connection,"SELECT rowid, source FROM reportable_data")
    for (rowid, sources) in collected_scources:
        if primary_inventory in sources.split(","):
            update_report_item_single_item(connection,"in_inventory", 1, rowid)
        else:
            update_report_item_single_item(connection,"in_inventory", 0, rowid)

def populate_report_table (connection:Connection, primary_inventory:str) -> None:
    columns = ("hostname", "fqdn", "ip", "mac")
    statement =  s_completed_rows(columns)
    table_name = "reportable_data"
    insert_select(connection, table_name, statement, columns)
    hostnames = field_select("hostname",table_name,columns)
    fqdns = field_select("fqdn",table_name,columns)
    ips = field_select("ip",table_name,columns)
    macs = field_select("mac",table_name,columns)

    for statement in (hostnames,fqdns,ips,macs):
        insert_select(connection,table_name,statement,columns)
        fill_nulls(connection)
    fill_source(connection)
    fill_in_inventory(connection,primary_inventory)