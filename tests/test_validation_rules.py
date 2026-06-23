from src.validation.rules import normalize_gender, valid_id, valid_score


def test_normalize_gender_variants() -> None:
    assert normalize_gender("F") == "Female"
    assert normalize_gender("female") == "Female"
    assert normalize_gender("M") == "Male"
    assert normalize_gender("unknown") is None


def test_valid_id_patterns() -> None:
    assert valid_id("student_id", "STU_00001")
    assert not valid_id("student_id", "BAD_STUDENT_001")
    assert valid_id("facilitator_id", "FAC_001")
    assert valid_id("collector_id", "COL_001")
    assert valid_id("device_id", "DEV_001")
    assert valid_id("module_id", "MOD_001")
    assert valid_id("survey_id", "SRV_000001")
    assert valid_id("intervention_id", "INT_00001")
    assert valid_id("source_upload_id", "UPL_00001")


def test_valid_score_range() -> None:
    assert valid_score(0)
    assert valid_score(100)
    assert not valid_score(132)
