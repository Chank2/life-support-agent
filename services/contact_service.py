import csv
from pathlib import Path

CONTACT_FILE = Path("data/contacts.csv")


def load_contacts():

    contacts = []

    if not CONTACT_FILE.exists():
        return contacts

    with open(CONTACT_FILE, "r", encoding="utf-8") as f:

        reader = csv.DictReader(f)

        for row in reader:
            contacts.append(row)

    return contacts
