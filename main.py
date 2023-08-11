from os.path import isfile, join
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
	from python.dbMaintainance import connect, insert_assets

	#verify existance of config file
	if not isfile("config.yml"):
		print("could not find config.yml. please create this file and fill the neccessary fields")
		quit(1)
		
	# Verify Database exists
	if not db_exists():
		from python.dbMaintainance import create_asset_table
		path = get_db_path()
		with open(path,"w") as fp:
			pass
		con = connect(path)
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
			case _:
	 			print(f"{source} has not yet been implimented")

	#insert list into DB
	print("Saving Data")
	db = connect(get_db_path())
	insert_assets(
		db,
		list(map(lambda x: x.to_tuple(),assets))
	)

	# run reports
	print ("Running Reports")

	from python.reports import report_discrepencies, report_new_assets, write_report_to_file, report_not_in_source, report_compare_two_sources

	print("\t reporting new devices")
	devices_discoverd_this_scan = report_new_assets(db)
	print("\tdone\n\tReporting devices that are only in one data source")
	devices_unique_to_datasource = report_discrepencies(db, CONFIG["data sources"])
	print(f"\tdone\n\tReporting devices not in {CONFIG['audit']['primary data source']}")
	devices_not_in_primary = report_not_in_source(db, CONFIG["audit"]["primary data source"])
	print("\tdone\n\n\tWriting reports to file")

	write_report_to_file("NewAssets",devices_discoverd_this_scan)
	write_report_to_file("PrimaryDelta",devices_not_in_primary)

	for k,v in devices_unique_to_datasource.items():
		write_report_to_file(f"Unique to {k}".replace(" ",""), v)