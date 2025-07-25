from datetime import datetime

class User:
    def __init__(self, username, password, role):
        self.username = username
        self.password = password
        self.role = role  # 'admin', 'attendant', 'owner'

class Slot:
    def __init__(self, slot_id, is_available=True, reserved=False, reserved_by=None):
        self.slot_id = int(slot_id)
        self.is_available = (is_available == 'True') if type(is_available)==str else is_available
        self.reserved = (reserved == 'True') if type(reserved)==str else reserved
        self.reserved_by = reserved_by

class Transaction:
    def __init__(self, vehicle_plate, owner, slot_id, in_time, out_time=None, fee=0):
        self.vehicle_plate = vehicle_plate
        self.owner = owner
        self.slot_id = int(slot_id)
        self.in_time = in_time
        self.out_time = out_time
        self.fee = float(fee)

class Attendance:
    def __init__(self, attendant, start_time, end_time=None):
        self.attendant = attendant
        self.start_time = start_time
        self.end_time = end_time

class Reservation:
    def __init__(self, slot_id, owner, reserve_time, expire_time):
        self.slot_id = int(slot_id)
        self.owner = owner
        self.reserve_time = reserve_time
        self.expire_time = expire_time
