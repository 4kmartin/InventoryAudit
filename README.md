# InventoryAudit
Pulls Disparate network inventories from various sources and captures a point in time, againt which deltas can be reported on

# Dependensies

- Python v 3.7 >
  - pip
  - pyTenable
  - SQLite3

- PowerShell 
  - DHCPServer Module
  - DNSServer Module

- Windows Server >= 2016
- User with the following permissions
  - Dns Admin
  - DHCP Admin
  - WinRMRemoteWMIUsers_

 > Note: These Scripts need to be ran with local admin rights to the DNS, DHCP and Domain Controller Servers