import csv, os
from modules.models import User
from modules.utils import hash_password, verify_password

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

def csv_path(filename):
    return f"{DATA_DIR}/{filename}"

class UserManager:
    def __init__(self):
        self.users = self.load_users()

    def load_users(self):
        path = csv_path("users.csv")
        if os.path.exists(path):
            with open(path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return [User(**row) for row in reader]
        admin = User("admin", hash_password("admin"), "admin")
        self.save_users([admin])
        return [admin]

    def save_users(self, users=None):
        users = users or self.users
        with open(csv_path("users.csv"), "w", newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["username", "password", "role"])
            writer.writeheader()
            for u in users:
                writer.writerow(u.__dict__)

    def find_user(self, username, password):
        for u in self.users:
            if u.username == username and verify_password(password, u.password):
                return u
        return None

    def add_user(self, username, password, role):
        hashed = hash_password(password)
        self.users.append(User(username, hashed, role))
        self.save_users()

    def username_exists(self, username):
        return any(u.username == username for u in self.users)

    def find_user_by_username(self, username):
        for user in self.users:
            if user.username == username:
                return user
        return None

    def delete_user(self, username):
        self.users = [user for user in self.users if user.username != username]
        self.save_users()

