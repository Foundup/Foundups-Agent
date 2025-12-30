
import os
import sys
import time
import subprocess
import logging
from modules.infrastructure.instance_lock.src.instance_manager import InstanceLock

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_stale_process():
    # Create a dummy python process that looks like a monitor
    # We use main.py in the command line args to mimic the monitor
    cmd = [sys.executable, "-c", "import time; time.sleep(60)", "main.py"]
    proc = subprocess.Popen(cmd)
    return proc

def test_lock_cleanup():
    print(f"Current PID: {os.getpid()}")
    
    # 1. Create a "stale" process
    stale_proc = create_stale_process()
    print(f"Created stale process: {stale_proc.pid}")
    
    # Wait a bit to ensure it's running
    time.sleep(1)
    
    # 2. Initialize lock (simulating main.py)
    # forcing ttl to 0 to make the process immediately stale
    lock = InstanceLock("test_monitor", ttl_minutes=0)
    
    # 3. Acquire lock (should trigger cleanup)
    print("Attempting to acquire lock (expecting cleanup)...")
    try:
        acquired = lock.acquire(auto_cleanup=True)
        print(f"Lock acquired: {acquired}")
    except Exception as e:
        print(f"Lock acquire failed with exception: {e}")
        
    print("Test finished.")
    
    # Cleanup if still alive
    if stale_proc.poll() is None:
        stale_proc.terminate()

if __name__ == "__main__":
    test_lock_cleanup()
