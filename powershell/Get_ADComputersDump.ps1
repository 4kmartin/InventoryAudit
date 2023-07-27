$OUTPUT_FILE = $args[0]

Import-Module ActiveDirectory

Get-ADComputer -filter * | Select-Object DNSHostName,Name|Export-Csv -path $OUTPUT_FILE
