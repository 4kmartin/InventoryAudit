import subprocess
import sys
from python.asset import Asset
from datetime import date

class ADAsset(Asset):

	def __init__ (self, hostname:str, fqdn:str) -> None:
		Asset.__init__(self,"Active Directory",hostname,fqdn,None,None)


class DNSAsset(Asset):
	def __init__ (self, hostname:str, ipaddress:str) -> None:
		Asset.__init__(self, "DNS", hostname, None, ipaddress, None)
	
	def set_fqdn (self, fqdn:str) -> None:
		self.fqdn = fqdn


class DHCPAsset (Asset):
	def __init__ (self, hostname:str, ipaddress:str):
		Asset.__init__(self, "DHCP", hostname, None, ipaddress, None)

		
def run_powershell_script(path_to_script:str, *arguments) :
	subprocess.Popen(["powershell","-NoProfile", path_to_script] + list(arguments), stdout=sys.stdout).communicate()


def get_ad_computers_dump(output_file_path:str)->list[ADAsset]:
	adassets =[]
	run_powershell_script("powershell\/Get_ADComputersDump.ps1", output_file_path)
	with open(output_file_path) as out:
		assets = out.readlines()
		out.close()
		for asset in assets[2:]:
			# print(asset)
			# quit(1)
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
		for asset in assets[2:]:
			name = asset.split(",")[0]
			ip = asset.split(",")[1]
			if dnsassets[-1].ip == ip:
				dnsassets[-1].set_fqdn(name)
			else:
				dnsassets.append(DNSAsset(name, ip))
	return dnsassets

def get_dhcp_dump (server:str, output_file:str) -> list[DHCPAsset]:
	dhcpassets = []
	run_powershell_script("powershell\/Get-DHCPDump.ps1", server, output_file)
	with open(output_file) as out:
		assets = out.readlines()
		out.close()
		for asset in assets[2:]:
			name = asset.split(",")[0]
			ip = asset.split(",")[1]
			dhcpassets.append(
				DHCPAsset(
					name,
					ip
				)
			)
	return dhcpassets