from tenable.io import TenableIO
from datetime import date

class TenableAsset:

    def __init__(self, host_name:str, fqdn:str, mac_addr:str, ip_addr:str):
        self.name = host_name
        self.fqdn = fqdn
        self.mac = mac_addr
        self.ip = ip_addr

    def to_tuple(self) ->tuple[str,int,str,str,str,str]:
        return ("tenable.io", date.today().toordinal(), self.name, self.fqdn, self.ip, self.mac)
        

def get_tenable_assets (access_key:str, secret_key:str) -> list[dict]:
    tio = TenableIO(access_key,secret_key)
    return filter_data(tio.assets.list())

def filter_data (asset_list:list[dict]) ->list[TenableAsset]:
    out = []
    for asset in asset_list:
        # print(asset["hostname"])
        try:
            host_name = asset["hostname"][-1]
        except IndexError:
            host_name = ""
        try:
            fqdn = asset["fqdn"][-1]
        except IndexError:
            fqdn = ""
        try:
            mac_addr = asset["mac_address"][-1]
        except IndexError:
            mac_addr = ""
        try:
            ip_addr = asset["ipv4"][-1]
        except IndexError:
            ip_addr = ""
        if (host_name,fqdn,mac_addr,ip_addr) == ("","","",""):
            continue
        out.append(TenableAsset(host_name,fqdn,mac_addr,ip_addr))
    return out

