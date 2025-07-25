import csv, os

DATA_DIR = "data"

def csv_path(filename):
    return f"{DATA_DIR}/{filename}"

class BlacklistManager:
    def __init__(self):
        self.blacklist = []
        self.blacklist = self.load_blacklist()

    def load_blacklist(self):
        path = csv_path("blacklist.csv")
        if os.path.exists(path):
            with open(path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return [row["vehicle_plate"] for row in reader]
        self.save_blacklist([])
        return []

    def save_blacklist(self, plates=None):
        plates = plates if plates is not None else self.blacklist
        with open(csv_path("blacklist.csv"), "w", newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["vehicle_plate"])
            writer.writeheader()
            for plate in plates:
                writer.writerow({"vehicle_plate": plate})

    def add_to_blacklist(self, plate):
        if plate not in self.blacklist:
            self.blacklist.append(plate)
            self.save_blacklist()

    def is_blacklisted(self, plate):
        return plate in self.blacklist