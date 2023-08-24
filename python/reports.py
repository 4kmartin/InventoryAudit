from python.dbMaintainance import _run_select_statement
from python.asset import Asset
from sqlite3 import Connection
from os.path import join


def write_report_to_file (report_name:str,query_output:list[tuple],description:str=""):
    report = f"{description}\nHostname, Fully Qualified Domain Name, IPv4 Address, MAC Address\n"
    for asset in query_output:
        report += ", ".join([str(i).replace(",","::") if i else "" for i in asset])
        report += "\n"
    file = join("csv",f"{report_name}.csv")
    with open(file, "w") as report_file:
        report_file.write(report)
        report_file.close()      

def report_newly_discovered_assets (connection:Connection, todays_date:int) -> list[Asset]:
    """reports on all assets that only appear in the database as of the most recent scan.
    todays_date field is the result of `datetime.date.today().toordinal()`"""
    pass

def report_assets_not_joined_to_domain (connection:Connection) -> list[Asset]:
    """requires either Active Directory or Azure Active Directory to be ingested as a data source"""
    pass

def report_has_company_antimalware (connection:Connection, antimalware_software:str) -> list[Asset]:
    """requires antimalware be ingested as a datasource"""
    pass

def report_not_found_in_company_asset_inventory (connection:Connection) -> list[Asset]:
    statement = "SELECT * FROM reportable_data WHERE in_inventory = 0 AND hostname NOT NULL"
    output = _run_select_statement(connection,statement)
    write_report_to_file("NotInventoried",output,"THESE REPORTED DEVICES WERE FOUND IN THE DATABASE OF A SOFTWARE USED BY THE COMPANY BUT NOT IN THE INVENTORY")