memory_store = {
    "last_task": None
}

def set_last_task(task_name: str):
    memory_store["last_task"] = task_name

def get_last_task():
    return memory_store.get("last_task")
