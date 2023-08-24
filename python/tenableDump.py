from tenable.io import TenableIO
from python.asset import Asset
from typing import Optional

class TenableAsset (Asset):

    def __init__(self, host_name:Optional[str], fqdn:Optional[str], ip_addr:Optional[str], mac_addr:Optional[str]) -> None:
        Asset.__init__(self, "Tenable", host_name, fqdn, ip_addr, mac_addr)
      

def get_tenable_assets (access_key:str, secret_key:str) -> list[dict]:
    tio = TenableIO(access_key,secret_key)
    return filter_data(tio.assets.list())

def filter_data (asset_list:list[dict]) ->list[TenableAsset]:
    out = []
    for asset in asset_list:
        # print(asset["hostname"])
        try:
            host_name = asset["hostname"][-1] if asset["hostname"] not in ("", " ") else None
        except IndexError:
            host_name = None
        try:
            fqdn = asset["fqdn"][-1] if asset["fqdn"][-1] not in (""," ") else None
        except IndexError:
            fqdn = None
        try:
            mac_addr = asset["mac_address"][-1] if asset["mac_address"][-1] not in (""," ") else None
        except IndexError:
            mac_addr = None
        try:
            ip_addr = asset["ipv4"][-1] if asset["ipv4"][-1] not in ("", " ") else None
        except IndexError:
            ip_addr = None
        if (host_name,fqdn,mac_addr,ip_addr) == (None, None, None, None):
            continue
        out.append(TenableAsset(host_name,fqdn,ip_addr,mac_addr))
    return out

