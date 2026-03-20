logs = []

def add_log(action: str):
    from datetime import datetime
    time = datetime.now().strftime("%H:%M:%S")
    logs.append(f"[{time}] {action}")

def get_logs():
    return logs[-10:]
