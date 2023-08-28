from typing import Optional
from typing_extensions import Self
from datetime import date


class Asset:

    def __init__(self, data_source: str, hostname: Optional[str], fqdn: Optional[str], ip: Optional[str],
                 mac: Optional[str]) -> None:
        self.hostname = sanitize_string_value(hostname)
        self.fqdn = sanitize_string_value(fqdn)
        self.ip = sanitize_string_value(ip)
        self.mac = sanitize_string_value(mac)
        self.date_discovered = date.today().toordinal()
        self.source = data_source

    def to_tuple(self) -> tuple[str, int, Optional[str], Optional[str], Optional[str], Optional[str]]:
        return self.source, self.date_discovered, self.hostname, self.fqdn, self.ip, self.mac

    def __eq__(self, other_asset: Self) -> bool:
        hostname_eq = self.hostname == other_asset.hostname and self.hostname is not None
        source_eq = self.source == other_asset.source and self.source is not None
        fqdn_eq = self.fqdn == other_asset.fqdn and self.fqdn is not None
        fn_hn_eq = self.fqdn is not None and self.fqdn == other_asset.hostname
        hn_fn_eq = self.hostname is not None and self.hostname == other_asset.fqdn
        cross_eq = fn_hn_eq or hn_fn_eq
        qualified_hn_eq = source_eq and hostname_eq
        qualified_fn_eq = source_eq and fqdn_eq
        qualified_cross = source_eq and cross_eq
        all_eq = source_eq and hostname_eq and fqdn_eq and self.ip == other_asset.ip and self.mac == other_asset.mac

        return all_eq or qualified_cross or qualified_fn_eq or qualified_hn_eq

    def __repr__(self) -> str:
        return f"Asset; source:{self.source} date:{date.fromordinal(self.date_discovered)} hostname:{self.hostname} fqdn:{self.fqdn} ip:{self.ip} mac:{self.mac}"


def sanitize_string_value(string: Optional[str]) -> Optional[str]:
    if string and string != "" and string != " ":
        string: str = string.lower().replace("\"", "").replace("\'", "") .replace("...", "").replace(":", "")
        # added this check in case string had a value like "''"
        if string != "" and string != " ":
            return string
        else:
            return None
    else:
        return None
