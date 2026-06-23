from __future__ import annotations

import hashlib
import json
from typing import Any


METADATA_FIELDS = {
    "_id",
    "_batch_id",
    "_ingested_at",
    "_source_file",
    "_record_hash",
    "_run_id",
    "_updated_at",
}


def compute_record_hash(record: dict[str, Any]) -> str:
    """
    Computes a stable SHA-256 hash of a dictionary, ignoring metadata fields.
    Useful for change detection (idempotent loading).
    """
    # Filter out metadata fields
    clean_record = {k: v for k, v in record.items() if k not in METADATA_FIELDS}
    
    # Convert to JSON with sorted keys to ensure stable output
    serialized = json.dumps(clean_record, sort_keys=True, separators=(",", ":"), default=str)
    
    # Compute SHA-256
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
