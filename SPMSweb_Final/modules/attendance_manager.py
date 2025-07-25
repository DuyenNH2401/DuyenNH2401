import csv, os
from models import Attendance

DATA_DIR = "data"

def csv_path(filename):
    return f"{DATA_DIR}/{filename}"

class AttendanceManager:
    def __init__(self):
        self.attendances = []  # Gán thuộc tính trước
        self.attendances = self.load_attendances()
    def load_attendances(self):
        path = csv_path("attendance.csv")
        if os.path.exists(path):
            with open(path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return [Attendance(**row) for row in reader]
        self.save_attendances([])   # Đã có self.attendances là []
        return []
    def save_attendances(self, attendances=None):
        attendances = attendances if attendances is not None else self.attendances
        with open(csv_path("attendance.csv"), "w", newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["attendant", "start_time", "end_time"])
            writer.writeheader()
            for a in attendances:
                writer.writerow(a.__dict__)

    def check_in(self, attendant):
        now = datetime.now().isoformat()
        self.attendances.append(Attendance(attendant, now))
        self.save_attendances()
    def check_out(self, attendant):
        for a in reversed(self.attendances):
            if a.attendant == attendant and not a.end_time:
                a.end_time = datetime.now().isoformat()
                self.save_attendances()
                return True
        return False
