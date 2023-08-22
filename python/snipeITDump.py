from requests import get, Response
from python.asset import Asset
from typing import Optional

class SnipeItAsset (Asset):

    def __init__(self, hostname:Optional[str], mac:Optional[str]) -> None:
        Asset.__init__(self, "Snipe-IT", hostname, None, None, mac)


def get_all_asset_names (snipe_it_url:str, personal_access_token:str) -> list[SnipeItAsset]:

    url = f"{snipe_it_url}/api/v1/hardware"

    headers = {
        "Accept":"application/json",
        "Content-Type":"application/json",
        "Authorization": f"Bearer {personal_access_token}"
    }

    assets = []
    offset = 0
    response = _paginated_get_req(url,headers,100, offset)

    while response.json()["total"] > offset:
        for asset in response.json()["rows"]:
            name = asset["name"] if asset["name"] != "" else None
            try:
                wifi_mac = asset["custom_fields"]["Wifi MAC address"]["value"]
            except KeyError:
                wifi_mac = ""
            try:
                eth_mac = asset["custom_fields"]["Ethernet MAC address"]["value"]
            except KeyError:
                eth_mac = ""
            mac = wifi_mac if wifi_mac != "" else eth_mac if eth_mac != "" else None
            if not (name, mac) == (None, None):
                assets.append(
                    SnipeItAsset(
                        name,
                        mac
                    )
                )
        offset += 100
    return assets

def _paginated_get_req (url:str, headers:dict[str,str],limit:int,offset:int) -> Response:
    modified_url = "{url}?limit={limit}&offset={offset}&sort=id&order=asc"
    return get(url, headers=headers)