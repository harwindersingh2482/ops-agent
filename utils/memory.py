memory_store = {
    "last_task": None,
    "last_options": None
}

def set_last_task(task_name: str):
    memory_store["last_task"] = task_name

def get_last_task():
    return memory_store.get("last_task")

def set_options(options: list):
    memory_store["last_options"] = options

def get_options():
    return memory_store.get("last_options")

def clear_options():
    memory_store["last_options"] = None
