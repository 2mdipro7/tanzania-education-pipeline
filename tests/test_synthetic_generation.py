import random

from faker import Faker

from src.generate_data.generate_all import generate_curriculum_modules, generate_schools


def test_generate_schools_includes_map_ready_fields() -> None:
    schools = generate_schools(Faker(), random.Random(42), count=3)

    assert len(schools) == 3
    for school in schools:
        assert "street_address" in school
        assert "ward" in school
        assert -12 <= school["latitude"] <= 0
        assert 28 <= school["longitude"] <= 42
        assert school["location"]["type"] == "Point"
        assert school["location"]["coordinates"] == [school["longitude"], school["latitude"]]


def test_generate_curriculum_modules_has_term2_sequence() -> None:
    modules = generate_curriculum_modules()

    assert len(modules) == 8
    assert modules[0]["module_id"] == "MOD_001"
    assert modules[-1]["week_number"] == 8
    assert all(module["term"] == "Term 2" for module in modules)

