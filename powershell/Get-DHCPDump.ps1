OUTPUT_FILE= $1
SERVER= $2

Get-DHCPServerv4Scope -ComputerName $SERVER | Get-DHCPServerv4Lease -ComputerName $SERVER | Export-CSV -Path $OUTPUT_FILE

