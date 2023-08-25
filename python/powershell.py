import subprocess
import sys
from python.asset import Asset
from os.path import join


class ADAsset(Asset):

    def __init__(self, hostname: str, fqdn: str) -> None:
        Asset.__init__(self, "Active Directory", hostname, fqdn, None, None)


class DNSAsset(Asset):
    def __init__(self, hostname: str, ipaddress: str) -> None:
        Asset.__init__(self, "DNS", hostname, None, ipaddress, None)

    def set_fqdn(self, fqdn: str) -> None:
        self.fqdn = fqdn


class DHCPAsset(Asset):
    def __init__(self, fqdn: str, ipaddress: str) -> None:
        Asset.__init__(self, "DHCP", None, fqdn, ipaddress, None)


def run_powershell_script(path_to_script: str, *arguments):
    subprocess.Popen(["powershell", "-NoProfile", path_to_script] + list(arguments), stdout=sys.stdout).communicate()


def get_ad_computers_dump(output_file_path: str) -> list[ADAsset]:
    ad_assets = []
    run_powershell_script(join("powershell", "Get_ADComputersDump.ps1"), output_file_path)
    with open(output_file_path) as out:
        assets = out.readlines()
        out.close()
        for asset in assets[2:]:
            # print(asset)
            # quit(1)
            name = asset.split(",")[1]
            fqdn = asset.split(",")[0]
            ad_assets.append(ADAsset(name, fqdn))
    return ad_assets


def get_dns_dump(zone: str, server: str, output_file: str) -> list[DNSAsset]:
    run_powershell_script(join("powershell", "Get-DnsDump.ps1"), zone, server, output_file)
    with open(output_file) as out:
        assets = out.readlines()
        out.close()
    return make_dns_assets(assets[1:])


def make_dns_assets(assets: list[str]) -> list[DNSAsset]:
    dns_assets = [DNSAsset(
        assets[0].split(",")[0],
        assets[0].split(",")[1]
    )]
    for asset in assets[1:]:
        name = asset.split(",")[0]
        ip = asset.split(",")[1]
        dns_asset: DNSAsset = DNSAsset(name, ip)
        if dns_assets[-1].hostname == dns_asset.hostname.split(".")[0] and dns_asset.ip == dns_assets[-1].ip:
            dns_assets[-1].set_fqdn(dns_asset.hostname)
        elif dns_asset in dns_assets:
            continue
        else:
            dns_assets.append(dns_asset)
    return dns_assets


def get_dhcp_dump(server: str, output_file: str) -> list[DHCPAsset]:
    dhcp_assets = []
    run_powershell_script(join("powershell", "Get-DHCPDump.ps1"), server, output_file)
    with open(output_file) as out:
        assets = out.readlines()
        out.close()
        for asset in assets[2:]:
            name = asset.split(",")[0]
            ip = asset.split(",")[1]
            dhcp_assets.append(
                DHCPAsset(
                    name,
                    ip
                )
            )
    return dhcp_assets
