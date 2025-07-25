import csv, os
from datetime import datetime, timedelta

DATA_DIR = "data"
def csv_path(filename):
    return f"{DATA_DIR}/{filename}"

class Transaction:
    def __init__(self, vehicle_plate, owner, slot_id, in_time, out_time=None, fee=0, paid=False):
        self.vehicle_plate = vehicle_plate
        self.owner = owner
        self.slot_id = int(slot_id)
        self.in_time = in_time
        self.out_time = out_time
        self.fee = float(fee)
        self.paid = (paid == 'True') if type(paid)==str else bool(paid)

class TransactionManager:
    def __init__(self, default_rate=2.0, dynamic_rates=None):
        self.transactions = []
        self.transactions = self.load_transactions()
        self.default_rate = default_rate
        self.dynamic_rates = dynamic_rates or {}

    def load_transactions(self):
        path = csv_path("transactions.csv")
        if os.path.exists(path):
            with open(path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return [Transaction(**row) for row in reader]
        self.save_transactions([])
        return []

    def save_transactions(self, txs=None):
        txs = txs if txs is not None else self.transactions
        with open(csv_path("transactions.csv"), "w", newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                "vehicle_plate", "owner", "slot_id", "in_time", "out_time", "fee", "paid"
            ])
            writer.writeheader()
            for t in txs:
                writer.writerow({
                    "vehicle_plate": t.vehicle_plate,
                    "owner": t.owner,
                    "slot_id": t.slot_id,
                    "in_time": t.in_time,
                    "out_time": t.out_time,
                    "fee": t.fee,
                    "paid": t.paid
                })

    def get_hourly_rate(self, dt):
        hour = dt.hour
        for (start, end), rate in self.dynamic_rates.items():
            if start < end:
                if start <= hour < end:
                    return rate
            else:
                if hour >= start or hour < end:
                    return rate
        return self.default_rate

    def check_in(self, plate, owner, slot_id):
        in_time = datetime.now().isoformat()
        self.transactions.append(Transaction(plate, owner, slot_id, in_time))
        self.save_transactions()

    def check_out(self, plate):
        for t in reversed(self.transactions):
            if t.vehicle_plate == plate and not t.out_time:
                t.out_time = datetime.now().isoformat()
                dt_in = datetime.fromisoformat(t.in_time)
                dt_out = datetime.fromisoformat(t.out_time)
                total_seconds = (dt_out - dt_in).total_seconds()
                total_hours = int(total_seconds // 3600)
                if total_seconds % 3600 > 0:
                    total_hours += 1
                fee = 0
                current = dt_in
                for _ in range(total_hours):
                    rate = self.get_hourly_rate(current)
                    fee += rate
                    current += timedelta(hours=1)
                t.fee = fee
                self.save_transactions()
                return t.fee, t.slot_id
        return None, None

    def get_revenue(self, from_date=None, to_date=None):
        total = 0
        for t in self.transactions:
            if t.fee and t.out_time:
                dt = datetime.fromisoformat(t.out_time)
                if (not from_date or dt >= from_date) and (not to_date or dt <= to_date):
                    total += t.fee
        return total

    def search_transactions(self, owner):
        return [t for t in self.transactions if t.owner == owner]

    def set_dynamic_rate(self, start, end, rate):
        self.dynamic_rates[(start, end)] = rate

    def get_unpaid_transactions(self, owner):
        return [t for t in self.transactions if t.owner == owner and t.fee > 0 and not t.paid]
