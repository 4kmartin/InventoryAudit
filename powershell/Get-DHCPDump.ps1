$OUTPUT_FILE= $args[1]
$SERVER= $args[0]

Get-DHCPServerv4Scope -ComputerName $SERVER | Get-DHCPServerv4Lease -ComputerName $SERVER | Select HostName, IPAddress | Export-CSV -Path $OUTPUT_FILE

