from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import get_settings
from src.db import get_database, ping


def main() -> None:
    settings = get_settings()
    result = ping()
    db = get_database()
    print(f"MongoDB ping: {result}")
    print(f"Database: {settings.mongo_db_name}")
    print(f"Collections: {db.list_collection_names()}")


if __name__ == "__main__":
    main()
