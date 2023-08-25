from typing import Optional

from tenable.io import TenableIO

from python.asset import Asset


class TenableAsset(Asset):

    def __init__(self, host_name: Optional[str], fqdn: Optional[str], ip: Optional[str],
                 mac: Optional[str]) -> None:
        Asset.__init__(self, "Tenable", host_name, fqdn, ip, mac)


def get_tenable_assets(access_key: str, secret_key: str) -> list[TenableAsset]:
    tio = TenableIO(access_key, secret_key)
    return filter_data(tio.assets.list())


def filter_data(asset_list: list[dict]) -> list[TenableAsset]:
    out = []
    for asset in asset_list:
        # print(asset["hostname"])
        try:
            host_name = asset["hostname"][-1] if asset["hostname"] not in ("", " ") else None
        except IndexError:
            host_name = None
        try:
            fqdn = asset["fqdn"][-1] if asset["fqdn"][-1] not in ("", " ") else None
        except IndexError:
            fqdn = None
        try:
            mac = asset["mac_address"][-1] if asset["mac_address"][-1] not in ("", " ") else None
        except IndexError:
            mac = None
        try:
            ip = asset["ipv4"][-1] if asset["ipv4"][-1] not in ("", " ") else None
        except IndexError:
            ip = None
        if (host_name, fqdn, mac, ip) == (None, None, None, None):
            continue
        out.append(TenableAsset(host_name, fqdn, ip, mac))
    return out
