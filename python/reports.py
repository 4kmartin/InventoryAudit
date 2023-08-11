from datetime import date
from python.dbMaintainance import _run_select_statement, collate_data, collate_from_source
from sqlite3 import Connection
from os.path import join

def report_new_assets (connection:Connection) -> list[tuple]:
    today = date.today().toordinal()
    statement = f"SELECT hostname,fqdn,ip,mac FROM discovered_assets WHERE datefound = {today} EXCEPT SELECT hostname,fqdn,ip,mac FROM discovered_assets WHERE datefound < {today}"
    return _run_select_statement(connection, statement)

def report_discrepencies (connection:Connection, data_sources:list[str]) -> dict[str,list[tuple]]:
    unique = {}
    for source in data_sources:
        unique += {source : report_unique_to(connection, source)}
    return unique

def report_unique_to(connection:Connection, source:str) -> list[tuple]:
    collate_data(connection, source)
    collate_from_source(connection, source)
    statement = f"SELECT name, fqdn, ip, mac FROM collated_from_{source} EXCEPT SELECT name,fqdn,ip,mac FROM collated_assets;"
    return _run_select_statement(connection, statement)

def write_report_to_file (report_name:str,query_output:list[tuple],description:str=""):
    report = f"{description}\nHostname, Fully Qualified Domain Name, IPv4 Address, MAC Address\n"
    for asset in query_output:
        report += ", ".join(asset)
        report += "\n"
    file = join("csv",f"{report_name}.csv")
    with open(file, "w") as report_file:
        report_file.write(report)
        report_file.close()
        
def report_not_in_source (connection:Connection, source:str) -> list[tuple]:
    collate_data(connection,source)
    collate_from_source(connection,source)
    statement = f"SELECT name FROM collated_assets WHERE name NOT IN collated_from_{source};"
    return _run_select_statement(statement)

def report_compare_two_sources (connection:Connection, source_1:str, source_2:str) -> dict[str,list[tuple]]:
    collate_from_source(connection,source_1)
    collate_from_source(connection, source_2)
    not_in_1 = f"SELECT name FROM collated_from_{source_2} WHERE name NOT IN collated_from_{source_1};"
    not_in_2 = f"SELECT name FROM collated_from_{source_1} WHERE name NOT IN collated_from_{source_2};"
    return {
        f"not in {source_1}": _run_select_statement(connection,not_in_1),
        f"not in {source_2}": _run_select_statement(connection,not_in_2)
    }
