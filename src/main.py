from pathlib import Path
from src.database import init_database

def setup():
    folders = [
        "data/raw",
        "data/processed",
        "data/sources",
        "output",
        "database",
    ]

    for folder in folders:
        Path(folder).mkdir(parents=True, exist_ok=True)

    init_database()
    print("Investment Research Copilot initialized.")

if __name__ == "__main__":
    setup()