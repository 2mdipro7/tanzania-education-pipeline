from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "generated"


@dataclass(frozen=True)
class Settings:
    mongo_uri: str
    mongo_db_name: str
    data_seed: int


def get_settings() -> Settings:
    load_dotenv(BASE_DIR / ".env")
    return Settings(
        mongo_uri=os.getenv(
            "MONGO_URI",
            "mongodb://admin:adminpassword@localhost:27017/?authSource=admin",
        ),
        mongo_db_name=os.getenv("MONGO_DB_NAME", "mewaka_program_metrics"),
        data_seed=int(os.getenv("DATA_SEED", "42")),
    )

