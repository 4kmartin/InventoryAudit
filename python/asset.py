from typing import Optional
from datetime import date


class Asset:

    def __init__(self, data_source:str, hostname:Optional[str], fqdn:Optional[str], ip:Optional[str], mac:Optional[str]) -> None :
        self.hostname = hostname.lower() if isinstance(hostname,str) else fqdn.split(".")[0] if isinstance(fqdn,str) else None
        self.fqdn = fqdn.lower() if isinstance(fqdn,str) else None
        self.ip = ip if isinstance(ip,str) else None
        self.mac = mac.replace(":","").replace("-","") if isinstance(mac, str) else None
        self.date_discovered = date.today().toordinal() 
        self.source = data_source
        
    def to_tuple(self) -> tuple[str, int, Optional[str], Optional[str], Optional[str], Optional[str]]:
        return (self.source, self.date_discovered, self.hostname, self.fqdn, self.ip, self.mac)
