from __future__ import annotations

from pymongo import MongoClient
from pymongo.database import Database

from src.config import get_settings


def get_client() -> MongoClient:
    settings = get_settings()
    return MongoClient(settings.mongo_uri, serverSelectionTimeoutMS=8000)


def get_database() -> Database:
    settings = get_settings()
    return get_client()[settings.mongo_db_name]


def ping() -> dict:
    client = get_client()
    try:
        return client.admin.command("ping")
    finally:
        client.close()

