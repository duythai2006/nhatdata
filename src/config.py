from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
SOURCES_DIR = DATA_DIR / "sources"

OUTPUT_DIR = ROOT / "output"
DATABASE_DIR = ROOT / "database"

for folder in [
    RAW_DIR,
    PROCESSED_DIR,
    SOURCES_DIR,
    OUTPUT_DIR,
    DATABASE_DIR,
]:
    folder.mkdir(parents=True, exist_ok=True)
