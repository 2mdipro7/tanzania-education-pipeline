from src.ingestion.record_hash import compute_record_hash


def test_hash_stability() -> None:
    record1 = {"b": 2, "a": 1}
    record2 = {"a": 1, "b": 2}
    assert compute_record_hash(record1) == compute_record_hash(record2)


def test_hash_excludes_metadata() -> None:
    record = {"id": "1", "value": 100}
    record_with_meta = {
        "id": "1",
        "value": 100,
        "_batch_id": "b1",
        "_ingested_at": "now",
        "_source_file": "file.json",
        "_run_id": "r1",
        "_updated_at": "now",
        "_record_hash": "abc",
    }
    assert compute_record_hash(record) == compute_record_hash(record_with_meta)


def test_hash_changes_with_content() -> None:
    assert compute_record_hash({"id": "1", "v": 1}) != compute_record_hash({"id": "1", "v": 2})
