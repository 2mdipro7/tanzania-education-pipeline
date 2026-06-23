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


def _get_streamlit_secret(key: str) -> str | None:
    """Read a secret from Streamlit's secrets store if running on Streamlit Cloud."""
    try:
        import streamlit as st  # noqa: PLC0415
        return st.secrets.get(key)
    except Exception:
        return None


def get_settings() -> Settings:
    load_dotenv(BASE_DIR / ".env")
    return Settings(
        mongo_uri=(
            _get_streamlit_secret("MONGO_URI")
            or os.getenv("MONGO_URI", "mongodb://admin:adminpassword@localhost:27017/?authSource=admin")
        ),
        mongo_db_name=(
            _get_streamlit_secret("MONGO_DB_NAME")
            or os.getenv("MONGO_DB_NAME", "mewaka_program_metrics")
        ),
        data_seed=int(os.getenv("DATA_SEED", "42")),
    )

