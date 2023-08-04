Import-Module DnsServer

$ZONE = $args[0]

$SERVER = $args[1]

$OUTPUT_FILE =$args[2]

Get-DnsServerResourceRecord -RRType "A" -ZoneName $ZONE -ComputerName $SERVER | Select -Property Hostname -ExpandProperty RecordData|Export-CSV -Path $OUTPUT_FILE