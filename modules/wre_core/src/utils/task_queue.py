# tools/wre/task_queue.py
import json
import uuid
from pathlib import Path
from datetime import datetime
import os

# Platform-specific import for file locking
if os.name != 'nt':
    import fcntl

# Define the path to the task queue file
QUEUE_FILE = Path(__file__).parent.parent.parent / "WRE_TASK_QUEUE.jsonl"
# Define a lock file
LOCK_FILE = Path(__file__).parent.parent.parent / "WRE_TASK_QUEUE.lock"

# --- Platform-specific file locking ---
# This is crucial for preventing race conditions when multiple agents
# might try to access the queue file at the same time.

class FileLock:
    def __enter__(self):
        self.lock_file_handle = open(LOCK_FILE, 'w')
        if os.name == 'nt':
            # On Windows, we can't use fcntl, but opening a file in write
            # mode often provides a basic level of locking against other
            # processes trying to write. It's not as robust.
            # A more robust solution might use a library like `msvcrt`.
            pass 
        else:
            fcntl.flock(self.lock_file_handle, fcntl.LOCK_EX)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if os.name != 'nt':
            fcntl.flock(self.lock_file_handle, fcntl.LOCK_UN)
        self.lock_file_handle.close()


def dispatch_task(agent_type: str, payload: dict) -> str:
    """
    Appends a new task to the task queue.

    Args:
        agent_type: The type of agent required (e.g., 'COMPLIANCE_AGENT').
        payload: The data required by the agent to perform the task.

    Returns:
        The unique ID of the dispatched task.
    """
    task_id = f"task_{uuid.uuid4().hex[:10]}"
    task = {
        "task_id": task_id,
        "agent_type": agent_type,
        "payload": payload,
        "status": "QUEUED",
        "dispatched_at": datetime.utcnow().isoformat(),
        "last_updated": datetime.utcnow().isoformat(),
    }
    
    with FileLock():
        with open(QUEUE_FILE, "a", encoding='utf-8') as f:
            f.write(json.dumps(task) + "\\n")
            
    return task_id

def retrieve_next_task():
    """
    Retrieves the oldest QUEUED task and marks it as PROCESSING.

    Returns:
        A dictionary representing the task, or None if no tasks are available.
    """
    with FileLock():
        if not QUEUE_FILE.exists():
            return None

        updated_lines = []
        retrieved_task = None

        with open(QUEUE_FILE, "r+", encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                task = json.loads(line)
                # Retrieve the first queued task that we haven't already seen
                if task["status"] == "QUEUED" and not retrieved_task:
                    task["status"] = "PROCESSING"
                    task["last_updated"] = datetime.utcnow().isoformat()
                    retrieved_task = task
                updated_lines.append(json.dumps(task) + "\\n")
            
            # Rewrite the entire file with the updated statuses
            f.seek(0)
            f.truncate()
            f.writelines(updated_lines)

    return retrieved_task 