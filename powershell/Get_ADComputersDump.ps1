OUTPUT_FILE = $1

Get-ADComputer -filter * | Select-Object DNSHostName,Name|Export-Csv -path $OUTPUT_FILE
