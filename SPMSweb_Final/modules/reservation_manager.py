import csv, os
from datetime import datetime, timedelta
from models import Reservation

DATA_DIR = "data"

def csv_path(filename):
    return f"{DATA_DIR}/{filename}"

class ReservationManager:
    class ReservationManager:
        def __init__(self):
            self.reservations = []
            self.reservations = self.load_reservations()

        def load_reservations(self):
            path = csv_path("reservations.csv")
            if os.path.exists(path):
                with open(path, newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    return [Reservation(**row) for row in reader]
            self.save_reservations([])  # Đảm bảo thuộc tính tồn tại
            return []

        def save_reservations(self, reservations=None):
            reservations = reservations if reservations is not None else self.reservations
            with open(csv_path("reservations.csv"), "w", newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=["slot_id", "owner", "reserve_time", "expire_time"])
                writer.writeheader()
                for r in reservations:
                    writer.writerow({
                        "slot_id": r.slot_id,
                        "owner": r.owner,
                        "reserve_time": r.reserve_time,
                        "expire_time": r.expire_time
                    })

    def add_reservation(self, slot_id, owner, duration_minutes=30):
        reserve_time = datetime.now()
        expire_time = reserve_time + timedelta(minutes=duration_minutes)
        self.reservations.append(
            Reservation(slot_id, owner, reserve_time.isoformat(), expire_time.isoformat())
        )
        self.save_reservations()
    def remove_expired(self):
        now = datetime.now()
        self.reservations = [r for r in self.reservations if datetime.fromisoformat(r.expire_time) > now]
        self.save_reservations()
    def get_active_reservation(self, owner):
        now = datetime.now()
        for r in self.reservations:
            if r.owner == owner and datetime.fromisoformat(r.expire_time) > now:
                return r
        return None
