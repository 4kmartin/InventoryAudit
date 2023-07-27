import subprocess
import sys
from python.asset import Asset
from datetime import date

class ADAsset(Asset):

	def __init__ (self, hostname, fqdn):
		self.hostname = hostname
		self.fqdn = fqdn

	def to_tuple (self) -> (str, int, str, str, str, str):
		return ("Active Directory", date.today().toordinal(), self.hostname, self.fqdn, "", "")

def run_powershell_script(path_to_script:str, *arguments) :
	subprocess.Popen(["pwsh","-NoProfile", path_to_script] + list(arguments), stdout=sys.stdout).communicate()

def get_ad_computers_dump(output_file_path:str)->list[ADAsset]:
	adassets =[]
	run_powershell_script("powershell\/Get_ADComputersDump.ps1", output_file_path)
	with open(output_file_path) as out:
		assets = out.readlines()
		out.close()
		for asset in assets:
			adassets.append(ADAsset(*asset.split(",")))
	return adassets
