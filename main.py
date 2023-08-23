from os.path import isfile, join
from python.dbMaintainance import get_db_connection, insert_all, create_report_table, create_asset_table, migrate_to_historical_data 
from os import name as os_name
import yaml

def db_exists() -> bool:
	return isfile(get_db_path())

def get_db_path() -> str:
	config = open_config()
	return config["database"]["path"]

def open_config() -> dict:
	with open("config.yml") as f:
		return yaml.load(f, Loader=yaml.FullLoader)
	
if __name__ == '__main__':
	
	#verify existance of config file
	if not isfile("config.yml"):
		print("could not find config.yml. please create this file and fill the neccessary fields")
		quit(1)
		
	# Verify Database exists
	if not db_exists():
		path = get_db_path()
		with open(path,"w") as fp:
			pass
		con = get_db_connection(path)
		create_asset_table(con)
		con.close()

	# Setup Constants
	CONFIG = open_config()

	# compile List of Assets
	print("Gathering Data")
	assets = [] 
	
	for source in CONFIG["data sources"]:
		match source:
			case "Tenable":
				from python.tenableDump import get_tenable_assets
				assets += get_tenable_assets(
						CONFIG["Tenable"]["access key"],
						CONFIG["Tenable"]["secret key"]
				)
			case "Malwarebytes":
				from python.malwarebytesDump import get_malwarebytes_assets
				mb = CONFIG["Malwarebytes"]
				assets += get_malwarebytes_assets(
					mb["groups"],
					mb["client id"],
					mb["client secret"],
					mb["account id"]
				)
			case "Active Directory":
				if os_name == "nt":
					from python.powershell import get_ad_computers_dump
					assets += get_ad_computers_dump(join("csv","ADOut.csv"))
				else:
					print(f"cannot run {source} query on non Windows OS")
			case "DNS":
				if os_name == "nt":
					from python.powershell import get_dns_dump
					dns = CONFIG["DNS"]
					assets += get_dns_dump(
						dns["zone"],
						dns["server"],
						join("csv","DNSOut.csv")
					)
				else:
					print(f"cannot run {source} query on non Windows OS")
			case "Snipe-IT":
				from python.snipeITDump import get_all_asset_names
				assets += get_all_asset_names(CONFIG["Snipe-IT"]["url"],CONFIG["Snipe-IT"]["personal access token"])
			case "DHCP":
				if os_name == "nt":
					from python.powershell import get_dhcp_dump
					dhcp = CONFIG["DHCP"]
					assets += get_dhcp_dump(
						dhcp["server"],
						join("csv","DHCPOut.csv")
					)

				else:
					print(f"cannot run {source} query on non Windows OS")
			case _:
	 			print(f"{source} has not yet been implimented")

	#insert list into DB
	print("Saving Data")
	db = get_db_connection(get_db_path())
	insert_all(
		db,
		"discovered_assets",
		list(map(lambda x: x.to_tuple(),assets)),
		("source","datefound","hostname","fqdn","ip","mac")
	)
	
	# run reports
	