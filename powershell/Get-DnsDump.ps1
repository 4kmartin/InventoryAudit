Import-Module DnsServer

$zone = $args[0]

$server = $args[1]

Get-DnsServerResourceRecord -ZoneName $zone -ComputerName $server | ForEach-Object {$_.RecordData.ipv4address.IpAddressToString , $_.HostName}
