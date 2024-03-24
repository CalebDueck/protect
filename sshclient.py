import subprocess

# runs the script that sshs into all the Pis and waits for successful completion
def run_powershell_script(ssh_connection_name, remote_directory):
    powershell_script_path = r'SSH_Run_Game.ps1'  

    # Construct the PowerShell command
    powershell_command = f"powershell -File {powershell_script_path} -sshConnectionName {ssh_connection_name} -remoteDirectory {remote_directory}"

    try:
        # Run the PowerShell script and capture the output
        result = subprocess.run(powershell_command, check=True, shell=True, text=True, capture_output=True)

        # Check if "Success" is in the output
        if "Success" in result.stdout:
            print("Script execution successful.")
        else:
            print("Script execution failed.")
            # Handle the failure as needed
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        # Handle the error as needed



