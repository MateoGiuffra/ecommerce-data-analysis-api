import psutil
import os

def kill_celery_processes():
    """
    Finds and terminates lingering Celery processes based on their name and command line.
    It finds parent processes with 'celery' in the command line and kills the entire process tree.
    """
    killed_pids = set()
    process_count = 0

    # First, find all parent processes related to Celery
    celery_parents = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # A process is considered a Celery-related parent if 'celery' is in its command line.
            # We exclude the script's own process.
            if proc.pid != os.getpid() and 'celery' in " ".join(proc.cmdline()).lower():
                celery_parents.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # Now, iterate through the found parents and terminate their entire process tree
    for parent in celery_parents:
        try:
            # Get all children of the parent process, recursively
            children = parent.children(recursive=True)
            
            # Add the parent itself to the list of processes to kill
            procs_to_kill = [parent] + children

            for p in procs_to_kill:
                if p.pid not in killed_pids:
                    print(f"Found Celery-related process: PID={p.pid}, Name='{p.name()}'")
                    p.kill()
                    killed_pids.add(p.pid)
                    print(f" -> Process {p.pid} killed.")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # The process might have been killed already as part of another tree
            print(f" -> Process {parent.pid} already terminated or access denied.")
            pass

    process_count = len(killed_pids)
    if process_count == 0:
        print("No running Celery processes found.")
    else:
        print(f"\nSuccessfully terminated {process_count} Celery-related process(es).")

if __name__ == "__main__":
    kill_celery_processes()
        