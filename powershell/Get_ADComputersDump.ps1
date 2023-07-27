$OUTPUT_FILE = $1

Import-Module ActiveDirectory

Get-ADComputer -filter * | Select-Object DNSHostName,Name|Export-Csv -path $OUTPUT_FILE
