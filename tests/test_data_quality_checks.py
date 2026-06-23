from datetime import datetime, timezone

from src.validation.data_quality_checks import REFERENCE_DATE, days_old, ratio


def test_ratio_handles_zero_denominator() -> None:
    assert ratio(1, 0) is None
    assert ratio(3, 6) == 0.5


def test_days_old_uses_reference_date() -> None:
    value = datetime(2026, 7, 15, tzinfo=timezone.utc)

    assert days_old(value, REFERENCE_DATE) == 5


def test_days_old_accepts_naive_datetimes() -> None:
    value = datetime(2026, 7, 19)

    assert days_old(value, REFERENCE_DATE) == 1

