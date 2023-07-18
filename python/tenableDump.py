from tenable.io import TenableIO

class TenableAsset:

    def __init__(self, host_name:str, fqdn:str, mac_addr:str, ip_addr:str) -> TenabbleAsset:
        self.name = host_name
        self.fqdn = fqdn
        self.mac = mac_addr
        self.ip = ip_addr
        

def get_tenable_assets (access_key:str, secret_key:str) -> List[Dict]:
    tio = TenableIO(access_key,secret_key)
    return tio.assets.list()

def filter_data (asset_list:List[Dict]) ->List[TennableAsset]:
    out = []
    for asset in assett_list:
        host_name = asset["hostname"][-1]
        fqdn = asset["fqdn"][-1]
        mac_addr = asset["mac_address"][-1]
        ip_addr = asset["ipv4"][-1]
        out.append(TennableAsset(host_name,fqdn,mac_addr,ip_addr))
    return out

