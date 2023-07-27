from os.path import isfile
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
				from python.powershell import get_ad_computers_dump
				assets += get_ad_computers_dump("csv\/ADOut.csv")
			case _:
	 			print(f"{source} has not yet been implimented")

	#insert list into DB
	db = connect(get_db_path())
	insert_assets(
		db,
		list(map(lambda x: x.to_tuple(),assets))
	)