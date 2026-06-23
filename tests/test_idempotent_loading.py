from unittest.mock import MagicMock, patch

from pymongo import UpdateOne

from src.ingestion.load_raw_collections import load_raw_collections


@patch("src.ingestion.load_raw_collections.read_json")
@patch("src.ingestion.load_raw_collections.get_database")
@patch("src.ingestion.load_raw_collections.Path.exists")
def test_load_raw_collections_idempotency(mock_exists: MagicMock, mock_get_db: MagicMock, mock_read_json: MagicMock) -> None:
    # Setup mock
    mock_exists.return_value = True
    
    # Mock read_json to only return one file's content and empty for others to keep test simple
    def side_effect_read_json(path):
        if "schools.json" in str(path):
            return [{"school_id": "SCH_1", "name": "School 1"}]
        return []
    
    mock_read_json.side_effect = side_effect_read_json

    # Mock DB collections
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db
    
    # First run: no existing records
    mock_collection = MagicMock()
    mock_collection.find.return_value = []
    mock_db.__getitem__.return_value = mock_collection
    
    stats = load_raw_collections()
    
    # Check that it did 1 insert
    assert stats["sources"]["raw_schools"]["inserted"] == 1
    assert stats["sources"]["raw_schools"]["updated"] == 0
    assert stats["sources"]["raw_schools"]["unchanged"] == 0
    
    # Check that bulk_write was called with an UpdateOne operation
    calls = mock_collection.bulk_write.call_args_list
    assert len(calls) > 0
    assert isinstance(calls[0][0][0][0], UpdateOne)

