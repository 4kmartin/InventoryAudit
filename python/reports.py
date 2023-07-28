from datetime import date
from python.dbMaintainance import _run_select_statement
from sqlite3 import Connection

def report_new_assets (connection:Connection) -> list[tuple]:
    today = date.today().toordinal()
    statement = f"SELECT hostname,fqdn,ip,mac FROM discovered_assets WHERE datefound = {today} EXCEPT SELECT hostname,fqdn,ip,mac FROM discovered_assets WHERE datefound < {today}"
    _run_select_statement(connection, statement)

def report_discrepencies (data_sources:list[str]) -> list[tuple]:
    pass
