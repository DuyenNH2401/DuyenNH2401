import csv, os
from datetime import datetime

DATA_DIR = "data"

def csv_path(filename):
    return f"{DATA_DIR}/{filename}"

class AuditLog:
    def __init__(self):
        pass
    def log(self, username, action, detail=""):
        path = csv_path("audit_log.csv")
        exist = os.path.exists(path)
        with open(path, "a", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not exist:
                writer.writerow(["time", "username", "action", "detail"])
            writer.writerow([datetime.now().isoformat(), username, action, detail])

    def load_logs(self):
        logs = []
        path = csv_path("audit_log.csv")
        if os.path.exists(path):
            with open(path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                logs = [row for row in reader]
        return logs