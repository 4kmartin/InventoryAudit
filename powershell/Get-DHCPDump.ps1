$OUTPUT_FILE= $args[0]
$SERVER= $args[1]

Get-DHCPServerv4Scope -ComputerName $SERVER | Get-DHCPServerv4Lease -ComputerName $SERVER | Select HostName, IPAddress | Export-CSV -Path $OUTPUT_FILE

