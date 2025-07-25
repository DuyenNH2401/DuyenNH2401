import csv, os
from modules.models import Slot

DATA_DIR = "data"

def csv_path(filename):
    return f"{DATA_DIR}/{filename}"

class SlotManager:
    def __init__(self):
        # Đảm bảo luôn có self.slots là [] trước khi dùng!
        self.slots = []
        self.slots = self.load_slots()
    def load_slots(self):
        path = csv_path("slots.csv")
        if os.path.exists(path):
            with open(path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return [Slot(**row) for row in reader]
        # self.slots đã tồn tại rồi nên sẽ không lỗi nữa
        self.save_slots([])
        return []
    def save_slots(self, slots=None):
        slots = slots if slots is not None else self.slots
        with open(csv_path("slots.csv"), "w", newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["slot_id", "is_available", "reserved", "reserved_by"])
            writer.writeheader()
            for s in slots:
                writer.writerow({
                    "slot_id": s.slot_id,
                    "is_available": s.is_available,
                    "reserved": s.reserved,
                    "reserved_by": s.reserved_by
                })
    def add_slot(self, n):
        last_id = self.slots[-1].slot_id if self.slots else 0
        for i in range(1, n+1):
            self.slots.append(Slot(last_id+i, True, False, None))
        self.save_slots()
    def remove_slot(self, slot_id):
        self.slots = [s for s in self.slots if s.slot_id != int(slot_id)]
        self.save_slots()
    def update_slot(self, slot_id, is_available):
        for s in self.slots:
            if s.slot_id == int(slot_id):
                s.is_available = is_available
                s.reserved = False
                s.reserved_by = None
        self.save_slots()
    def reserve_slot(self, slot_id, owner):
        for s in self.slots:
            if s.slot_id == int(slot_id) and s.is_available and not s.reserved:
                s.reserved = True
                s.reserved_by = owner
                self.save_slots()
                return True
        return False
    def release_reserved_slot(self, slot_id):
        for s in self.slots:
            if s.slot_id == int(slot_id):
                s.reserved = False
                s.reserved_by = None
                self.save_slots()
    def get_available_slots(self):
        return [s for s in self.slots if s.is_available and not s.reserved]
    def get_reserved_slots(self):
        return [s for s in self.slots if s.reserved]
