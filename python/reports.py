from datetime import date
from python.dbMaintainance import _run_select_statement
from sqlite3 import Connection
from os.path import join

def report_new_assets (connection:Connection) -> list[tuple]:
    today = date.today().toordinal()
    statement = f"SELECT hostname,fqdn,ip,mac FROM discovered_assets WHERE datefound = {today} EXCEPT SELECT hostname,fqdn,ip,mac FROM discovered_assets WHERE datefound < {today}"
    return _run_select_statement(connection, statement)

def report_discrepencies (connection:Connection, data_sources:list[str]) -> list[tuple]:
    unique = []
    for source in data_sources:
        unique += report_unique_to(connection, source)
    return unique

def report_unique_to(connection:Connection, source:str) -> list[tuple]:
    statement = f"SELECT hostname, fqdn, ip, mac FROM discovered_assets WHERE source = '{source}' EXCEPT SELECT hostname,fqdn,ip,mac FROM discovered_assets WHERE source != '{source}'"
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
        
