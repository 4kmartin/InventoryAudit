from typing import Optional
from typing_extensions import Self
from datetime import date


class Asset:

    def __init__(self, data_source:str, hostname:Optional[str], fqdn:Optional[str], ip:Optional[str], mac:Optional[str]) -> None :
        self.hostname = hostname.lower().replace("\"","").replace("\'","") if isinstance(hostname,str) else fqdn.split(".")[0] if isinstance(fqdn,str) else None
        self.fqdn = fqdn.lower().replace("\"","").replace("\'","") if isinstance(fqdn,str) else None
        self.ip = ip.replace("\"","").replace("\'","") if isinstance(ip,str) else None
        self.mac = mac.replace(":","").replace("-","") if isinstance(mac, str) else None
        self.date_discovered = date.today().toordinal() 
        self.source = data_source
        
    def to_tuple(self) -> tuple[str, int, Optional[str], Optional[str], Optional[str], Optional[str]]:
        return (self.source, self.date_discovered, self.hostname, self.fqdn, self.ip, self.mac)

    def __eq__(self, other_asset:Self) -> bool:
        hostname_eq = self.hostname == other_asset.hostname and self.hostname is not None
        source_eq = self.source == other_asset.source and self.source is not None
        fqdn_eq = self.fqdn == other_asset.fqdn and self.fqdn is not None
        fn_hn_eq = self.fqdn is not None and self.fqdn == other_asset.hostname
        hn_fn_eq = self.hostname is not None and self.hostname == other_asset.fqdn
        cross_eq = fn_hn_eq or hn_fn_eq
        qualified_hn_eq = source_eq and hostname_eq
        qualified_fn_eq  = source_eq and fqdn_eq
        qualified_cross = source_eq and cross_eq
        all_eq = source_eq and hostname_eq and fqdn_eq and self.ip == other_asset.ip and self.mac == other_asset.mac 

        return all_eq or qualified_cross or qualified_fn_eq or qualified_hn_eq
