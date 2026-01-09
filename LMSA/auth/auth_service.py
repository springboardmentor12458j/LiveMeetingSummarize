import csv
from pathlib import Path

USER_FILE = Path("data/db/users.csv")
USER_FILE.parent.mkdir(exist_ok=True)

def user_exists(email):
    if not USER_FILE.exists():
        return False
    with open(USER_FILE, newline="") as f:
        return any(row["email"] == email for row in csv.DictReader(f))

def register_user(email, password):
    file_exists = USER_FILE.exists()
    with open(USER_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["email", "password"])
        writer.writerow([email, password])

def validate_user(email, password):
    if not USER_FILE.exists():
        return False
    with open(USER_FILE, newline="") as f:
        return any(
            row["email"] == email and row["password"] == password
            for row in csv.DictReader(f)
        )
