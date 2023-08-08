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


class DNSAsset(Asset):
	def __init__ (self, hostname, ipaddress):
		self.hostname = hostname
		self.ip = ipaddress

	def to_tuple(self) -> tuple[str, int, str, str, str, str]:
		return ("DNS", date.today().toordinal(),self.hostname,"",self.ip,"")

		
def run_powershell_script(path_to_script:str, *arguments) :
	subprocess.Popen(["powershell","-NoProfile", path_to_script] + list(arguments), stdout=sys.stdout).communicate()

def get_ad_computers_dump(output_file_path:str)->list[ADAsset]:
	adassets =[]
	run_powershell_script("powershell\/Get_ADComputersDump.ps1", output_file_path)
	with open(output_file_path) as out:
		assets = out.readlines()
		out.close()
		for asset in assets:
			print(asset)
			quit(1)
			name = asset.split(",")[1]
			fqdn = asset.split(",")[0]
			adassets.append(ADAsset(name,fqdn))
	return adassets

def get_dns_dump(zone:str, server:str, output_file:str) -> list[DNSAsset]:
	dnsassets =[]
	run_powershell_script("powershell\/Get-DnsDump.ps1", zone, server, output_file)
	with open(output_file) as out:
		assets = out.readlines()
		out.close()
		for asset in assets:
			name = asset.split(",")[0]
			ip = asset.split(",")[1]
			dnsassets.append(DNSAsset(name, ip))
	return dnsassets