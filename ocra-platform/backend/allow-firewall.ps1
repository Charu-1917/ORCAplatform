# Lets other PCs and phones on your network open ORCA (TCP port 8000).
# Run ONCE in PowerShell as Administrator:
#   powershell -ExecutionPolicy Bypass -File allow-firewall.ps1
# Remove later with:
#   Remove-NetFirewallRule -DisplayName "ORCA Backend 8000"

if (-not (Get-NetFirewallRule -DisplayName "ORCA Backend 8000" -ErrorAction SilentlyContinue)) {
    New-NetFirewallRule -DisplayName "ORCA Backend 8000" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow -Profile Private,Public
    Write-Host "Firewall rule added: TCP 8000 inbound allowed."
} else {
    Write-Host "Firewall rule already exists."
}
