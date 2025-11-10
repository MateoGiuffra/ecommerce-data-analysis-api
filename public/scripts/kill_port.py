import os
import sys
import subprocess
import platform

def kill_process_on_port(port: int):
    """
    Finds and kills a process running on a given port.
    Works on Windows, Linux, and macOS.
    """
    system = platform.system().lower()
    try:
        if system == "windows":
            command = f"netstat -a -n -o | findstr :{port}"
            output = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.DEVNULL)
            for line in output.strip().split('\n'):
                if "LISTENING" in line:
                    pid = line.split()[-1]
                    if pid.isdigit() and int(pid) > 0:
                        print(f"Windows: Found process with PID {pid} on port {port}. Killing it...")
                        subprocess.run(f"taskkill /F /PID {pid}", shell=True, check=True, capture_output=True)
                        print(f"Process {pid} killed.")
                        return
        elif system in ["linux", "darwin"]:
            command = f"lsof -ti:{port}"
            output = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.DEVNULL)
            pid = output.strip()
            if pid:
                print(f"{system.capitalize()}: Found process with PID {pid} on port {port}. Killing it...")
                subprocess.run(f"kill -9 {pid}", shell=True, check=True, capture_output=True)
                print(f"Process {pid} killed.")
    except subprocess.CalledProcessError:
        print(f"No process found running on port {port}.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        print("Usage: python scripts/kill_port.py <port>")
        sys.exit(1)
    
    kill_process_on_port(int(sys.argv[1]))