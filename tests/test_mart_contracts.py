from src.transformations.contract_tests import MART_CONTRACTS, duplicate_key_pipeline


def test_school_performance_contract_includes_map_fields() -> None:
    contract = MART_CONTRACTS["mart_school_performance"]

    assert "latitude" in contract["required_fields"]
    assert "longitude" in contract["required_fields"]
    assert contract["geojson_field"] == "location"


def test_all_mart_contracts_define_primary_keys() -> None:
    for contract in MART_CONTRACTS.values():
        assert contract["primary_key"]


def test_duplicate_key_pipeline_groups_by_primary_key() -> None:
    pipeline = duplicate_key_pipeline(["region", "district"])

    assert pipeline[0]["$group"]["_id"] == {
        "region": "$region",
        "district": "$district",
    }
    assert pipeline[1]["$match"] == {"count": {"$gt": 1}}
