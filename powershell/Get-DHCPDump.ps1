OUTPUT_FILE= $1
SERVER= $2

Get-DHCPServer4Scope -ComputerName $SERVER | Get-DHCPServer4Leases -ComputerName $SERVER | Export-CSV -Path $OUTPUT_FILE

