param(
    [string]$sshConnectionName
)

# Check if the ssh connection name is provided
if (-not $sshConnectionName) {
    Write-Host "Please provide the name of the SSH connection."
    exit 1
}
$remoteDirectory = "./Documents/Hubert/protect/server"
# Construct the SSH command with X11 forwarding, DISPLAY export, suppressing warnings, and remote script execution
$sshCommand = "ssh -F $env:USERPROFILE\.ssh\config -X -t $sshConnectionName 'export DISPLAY=:0; cd $remoteDirectory; nohup ./pygame_run.sh'"
Invoke-Expression -Command $sshCommand  

# Check if the SSH command was successful
if ($LASTEXITCODE -eq 0) {
    Write-Host "Success"
} else {
    Write-Host "Failed to run pygame script over SSH."
}
