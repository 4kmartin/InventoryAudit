import subprocess
import sys


def run_powershell_script(path_to_script:str, *arguments) -> str:
	return subprocess.Popen(["pwsh", path_to_script] + list(arguments), stdout=sys.stdout).communicate()

def get_ad_computers_dump(output_file_path:str)->str:
	return run_powershell_script("powershell\/Get_ADComputersDump.ps1", output_file_path)
