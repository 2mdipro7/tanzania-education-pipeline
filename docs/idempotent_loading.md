# Idempotent Loading Strategy

To support reproducible pipelines and incremental loads, the raw and clean layers use an **idempotent upsert strategy** instead of delete-and-replace.

## How It Works
1. **Primary Keys**: Each collection has a defined natural primary key (e.g., `school_id` for `raw_schools`).
2. **Record Hashing**: When a record is ingested, we compute a stable SHA-256 hash of its contents (excluding metadata fields like `_batch_id` and `_ingested_at`). This is stored as `_record_hash`.
3. **Change Detection**:
   - If a record with the same primary key does not exist → **Insert**
   - If a record exists but the `_record_hash` matches → **Skip (Unchanged)**
   - If a record exists and the `_record_hash` differs → **Update**

## Benefits
- Rerunning the pipeline on the same data results in 0 updates (safe).
- We can track exactly how many records were inserted vs. updated in a given run.
- Preserves historical `_ingested_at` timestamps for unchanged records, while updating `_updated_at` for modified ones.
