from requests import get, Response
from python.asset import Asset
from datetime import date


class SnipeItAsset (Asset):

    def __init__(self, name, mac):
        self.hostname = name
        self.mac = mac

    def to_tuple(self) -> tuple(str,int,str,str,str,str):
        return ("Snipe-IT", date.today().toordinal(), self.hostname, "", "", self.mac)


def get_all_asset_names (snipe_it_url:str, personal_access_token:str) -> list[SnipeITAsset]:

    url = f"{snipe_it_url}/api/v1/hardware"

    headers = {
        "Accept":"application/json",
        "Content-Type":"application/json",
        "Authorization": f"Bearer {personal_access_token}"
    }

    assets = []
    offset = 0
    response = _paginated_get_req(url,headers,100, offset)

    while response.json()["total"] > offset + 100:
        for asset in response.json()["rows"]:
            name = asset["name"]
            wifi_mac = asset["custom_fields"]["Wifi MAC address"]["value"]
            eth_mac = asset["custom_fields"]["Ethernet MAC address"]["value"]
            mac = wifi_mac if wifi_mac != "" else eth_mac
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