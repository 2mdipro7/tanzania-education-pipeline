from __future__ import annotations

import json
import random
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from faker import Faker

from src.config import DATA_DIR, get_settings


REGION_PROFILES = {
    "Arusha": {
        "districts": {
            "Arusha City": {"lat": -3.3869, "lon": 36.6830, "urban": 0.88, "risk": 0.86},
            "Meru": {"lat": -3.2460, "lon": 36.8650, "urban": 0.42, "risk": 0.95},
            "Karatu": {"lat": -3.3414, "lon": 35.6690, "urban": 0.35, "risk": 0.98},
        }
    },
    "Dar es Salaam": {
        "districts": {
            "Ilala": {"lat": -6.8161, "lon": 39.2804, "urban": 0.97, "risk": 0.82},
            "Kinondoni": {"lat": -6.7845, "lon": 39.2501, "urban": 0.98, "risk": 0.80},
            "Temeke": {"lat": -6.8598, "lon": 39.3108, "urban": 0.92, "risk": 0.88},
        }
    },
    "Dodoma": {
        "districts": {
            "Dodoma Urban": {"lat": -6.1630, "lon": 35.7516, "urban": 0.82, "risk": 0.89},
            "Chamwino": {"lat": -6.1960, "lon": 36.0200, "urban": 0.28, "risk": 1.07},
            "Kongwa": {"lat": -6.2007, "lon": 36.4198, "urban": 0.26, "risk": 1.10},
        }
    },
    "Mwanza": {
        "districts": {
            "Nyamagana": {"lat": -2.5164, "lon": 32.9175, "urban": 0.90, "risk": 0.84},
            "Ilemela": {"lat": -2.4800, "lon": 32.9300, "urban": 0.76, "risk": 0.90},
            "Magu": {"lat": -2.5833, "lon": 33.4333, "urban": 0.25, "risk": 1.12},
        }
    },
    "Mbeya": {
        "districts": {
            "Mbeya City": {"lat": -8.9094, "lon": 33.4608, "urban": 0.82, "risk": 0.90},
            "Rungwe": {"lat": -9.2500, "lon": 33.6500, "urban": 0.30, "risk": 1.08},
            "Mbarali": {"lat": -8.8500, "lon": 34.0200, "urban": 0.22, "risk": 1.14},
        }
    },
}

WARD_NAMES = [
    "Kati",
    "Mlimani",
    "Majengo",
    "Mabatini",
    "Nyerere",
    "Uhuru",
    "Sokoine",
    "Mji Mpya",
    "Kijitonyama",
    "Mwananyamala",
    "Iganzo",
    "Iyunga",
]

STREET_NAMES = [
    "Nyerere Road",
    "Uhuru Street",
    "Sokoine Avenue",
    "Market Road",
    "School Lane",
    "Mlimani Road",
    "Station Road",
    "Community Road",
    "Hospital Road",
    "Bus Stand Road",
]

CURRICULUM_BLUEPRINT = [
    ("MOD_001", "Entrepreneurship Basics", "Entrepreneurship", 1, 90, ["student workbook"]),
    ("MOD_002", "Savings and Budgeting", "Financial Literacy", 2, 90, ["budget worksheet"]),
    ("MOD_003", "Problem Solving", "Life Skills", 3, 80, ["scenario cards"]),
    ("MOD_004", "Communication Practice", "Communication", 4, 80, ["role-play guide"]),
    ("MOD_005", "Market Research", "Entrepreneurship", 5, 100, ["market survey template"]),
    ("MOD_006", "Business Planning", "Entrepreneurship", 6, 100, ["business canvas"]),
    ("MOD_007", "Leadership Lab", "Leadership", 7, 90, ["team challenge cards"]),
    ("MOD_008", "Pitch Preparation", "Communication", 8, 100, ["pitch rubric"]),
]

GUARDIAN_OCCUPATIONS = [
    "Small business owner",
    "Farmer",
    "Teacher",
    "Market vendor",
    "Driver",
    "Tailor",
    "Fishing worker",
    "Construction worker",
    "Healthcare worker",
    "Unemployed",
]

ABSENCE_REASONS = [
    "Illness",
    "Family duties",
    "Transport issue",
    "Fees issue",
    "Market or paid work",
    "Rain or weather",
    "Unknown",
]

FEEDBACK_SNIPPETS = [
    "I liked the group work and business examples.",
    "The sessions helped me understand saving money.",
    "I want more time for pitch practice.",
    "Transport makes it hard to attend every week.",
    "The facilitator explains the activities clearly.",
    "The workbook is useful but sometimes arrives late.",
]


def iso_day(value: date | None) -> str | None:
    return value.isoformat() if value else None


def iso_dt(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def rand_phone(rng: random.Random) -> str:
    return f"+255 7{rng.randint(10, 99)} {rng.randint(100, 999)} {rng.randint(100, 999)}"


def write_json(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(rows, file, indent=2, default=str)


def district_profile(region: str, district: str) -> dict[str, float]:
    return REGION_PROFILES[region]["districts"][district]


def generate_curriculum_modules() -> list[dict[str, Any]]:
    modules = []
    for module_id, module_name, competency_area, week_number, duration, materials in CURRICULUM_BLUEPRINT:
        modules.append(
            {
                "module_id": module_id,
                "module_name": module_name,
                "term": "Term 2",
                "week_number": week_number,
                "competency_area": competency_area,
                "expected_duration_minutes": duration,
                "required_materials": materials,
                "is_core_module": True,
                "prerequisite_module_id": None if week_number == 1 else f"MOD_{week_number - 1:03d}",
            }
        )
    return modules


def generate_schools(fake: Faker, rng: random.Random, count: int = 36) -> list[dict[str, Any]]:
    schools = []
    regions = list(REGION_PROFILES)
    for index in range(1, count + 1):
        region = rng.choice(regions)
        district = rng.choice(list(REGION_PROFILES[region]["districts"]))
        profile = district_profile(region, district)
        urban_rural = "Urban" if rng.random() < profile["urban"] else "Rural"
        latitude = round(profile["lat"] + rng.uniform(-0.12, 0.12), 6)
        longitude = round(profile["lon"] + rng.uniform(-0.12, 0.12), 6)
        electricity_chance = 0.92 if urban_rural == "Urban" else 0.64
        internet_chance = 0.82 if urban_rural == "Urban" else 0.38
        teacher_count = rng.randint(22, 54) if urban_rural == "Urban" else rng.randint(9, 28)
        schools.append(
            {
                "school_id": f"SCH_{index:03d}",
                "school_name": f"{fake.city()} Secondary School",
                "region": region,
                "district": district,
                "ward": rng.choice(WARD_NAMES),
                "street_address": f"Plot {rng.randint(1, 998)}, {rng.choice(STREET_NAMES)}",
                "postal_code": f"{rng.randint(10000, 89999)}",
                "latitude": latitude,
                "longitude": longitude,
                "location": {"type": "Point", "coordinates": [longitude, latitude]},
                "school_type": rng.choice(["Government", "Community", "Private"]),
                "urban_rural": urban_rural,
                "ownership": rng.choice(["Public", "Faith-based", "Private nonprofit", "Private"]),
                "head_teacher_name": fake.name(),
                "head_teacher_phone": rand_phone(rng),
                "student_capacity": rng.randint(450, 1300),
                "number_of_teachers": teacher_count,
                "electricity_available": rng.random() < electricity_chance,
                "internet_available": rng.random() < internet_chance,
                "has_projector": rng.random() < (0.62 if urban_rural == "Urban" else 0.25),
                "has_library": rng.random() < (0.58 if urban_rural == "Urban" else 0.34),
                "water_access": rng.choices(["Reliable", "Intermittent", "Limited"], [0.62, 0.28, 0.10])[0],
                "program_start_date": iso_day(date(2026, 1, 8) + timedelta(days=rng.randint(0, 24))),
                "implementation_status": rng.choices(
                    ["Active", "Needs Support", "Paused"],
                    [0.84, 0.13, 0.03],
                )[0],
                "school_context_risk": round(profile["risk"] * (1.08 if urban_rural == "Rural" else 0.94), 3),
            }
        )
    return schools


def generate_facilitators(fake: Faker, rng: random.Random, schools: list[dict[str, Any]]) -> list[dict[str, Any]]:
    school_groups: dict[tuple[str, str], int] = {}
    for school in schools:
        key = (school["region"], school["district"])
        school_groups[key] = school_groups.get(key, 0) + 1

    facilitators = []
    index = 1
    for (region, district), school_count in school_groups.items():
        facilitator_slots = max(1, round(school_count / 4))
        for _ in range(facilitator_slots):
            facilitators.append(
                {
                    "facilitator_id": f"FAC_{index:03d}",
                    "full_name": fake.name(),
                    "region": region,
                    "primary_district": district,
                    "assigned_districts": [district],
                    "phone": rand_phone(rng),
                    "email": fake.email(),
                    "hire_date": iso_day(date(2024, 1, 1) + timedelta(days=rng.randint(0, 700))),
                    "status": rng.choices(["Active", "On Leave", "Inactive"], [0.90, 0.07, 0.03])[0],
                    "supervisor_id": f"SUP_{rng.randint(1, 4):03d}",
                    "caseload_school_count": 0,
                    "home_base_latitude": round(district_profile(region, district)["lat"] + rng.uniform(-0.05, 0.05), 6),
                    "home_base_longitude": round(district_profile(region, district)["lon"] + rng.uniform(-0.05, 0.05), 6),
                }
            )
            index += 1
    return facilitators


def assign_facilitators(
    rng: random.Random,
    schools: list[dict[str, Any]],
    facilitators: list[dict[str, Any]],
) -> None:
    for school in schools:
        eligible = [
            facilitator
            for facilitator in facilitators
            if facilitator["region"] == school["region"]
            and facilitator["primary_district"] == school["district"]
            and facilitator["status"] == "Active"
        ]
        if not eligible:
            eligible = [facilitator for facilitator in facilitators if facilitator["region"] == school["region"]]
        facilitator = min(eligible, key=lambda item: item["caseload_school_count"])
        school["facilitator_id"] = facilitator["facilitator_id"]
        facilitator["caseload_school_count"] += 1


def generate_data_collectors(
    fake: Faker,
    rng: random.Random,
    facilitators: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    collectors = []
    for index, facilitator in enumerate(facilitators, start=1):
        collectors.append(
            {
                "collector_id": f"COL_{index:03d}",
                "full_name": fake.name(),
                "role": rng.choice(["Facilitator", "M&E Assistant", "School Focal Teacher"]),
                "assigned_region": facilitator["region"],
                "assigned_district": facilitator["primary_district"],
                "phone": rand_phone(rng),
                "supervisor_id": facilitator["supervisor_id"],
                "active": rng.random() > 0.04,
            }
        )
    return collectors


def generate_field_devices(
    rng: random.Random,
    collectors: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    devices = []
    for index, collector in enumerate(collectors, start=1):
        district = collector["assigned_district"]
        region = collector["assigned_region"]
        profile = district_profile(region, district)
        connectivity = rng.choices(
            ["Good", "Intermittent", "Poor"],
            [profile["urban"] * 0.62 + 0.18, 0.32, 0.50 - profile["urban"] * 0.30],
        )[0]
        last_sync = datetime(2026, 7, 20, 8, 0, tzinfo=timezone.utc) - timedelta(
            hours=rng.randint(1, 120 if connectivity == "Poor" else 48)
        )
        devices.append(
            {
                "device_id": f"DEV_{index:03d}",
                "assigned_to": collector["collector_id"],
                "assigned_region": region,
                "assigned_district": district,
                "device_model": rng.choice(["Samsung A14", "Tecno Spark", "Infinix Hot", "Nokia C32"]),
                "os_version": rng.choice(["Android 12", "Android 13", "Android 14"]),
                "connectivity_quality": connectivity,
                "last_sync_at": iso_dt(last_sync),
                "battery_health": rng.randint(62, 100),
                "app_version": rng.choice(["2.3.1", "2.3.2", "2.4.0"]),
            }
        )
    return devices


def generate_students(
    fake: Faker,
    rng: random.Random,
    schools: list[dict[str, Any]],
    count: int = 1260,
) -> list[dict[str, Any]]:
    gender_variants = ["Female", "Male", "female", "male", "F", "M"]
    students = []
    for index in range(1, count + 1):
        school = rng.choice(schools)
        risk_multiplier = school["school_context_risk"]
        age = rng.choices([14, 15, 16, 17, 18, 19, 20, 21], [0.02, 0.14, 0.23, 0.24, 0.20, 0.11, 0.05, 0.01])[0]
        enrollment_date = date(2026, 1, 8) + timedelta(days=rng.randint(0, 32))
        distance = round(clamp(rng.lognormvariate(0.9 if school["urban_rural"] == "Urban" else 1.3, 0.55), 0.2, 18.0), 1)
        has_phone_access = rng.random() < (0.76 if school["urban_rural"] == "Urban" else 0.47)
        baseline_score = round(clamp(rng.gauss(56, 16) - (distance * 0.9) + (8 if has_phone_access else 0), 10, 96), 1)
        dropout_probability = clamp(0.025 * risk_multiplier + (distance / 110) + (0.025 if not has_phone_access else 0), 0.02, 0.18)
        transfer_probability = 0.045 if school["urban_rural"] == "Urban" else 0.025
        status = rng.choices(
            ["Active", "Transferred", "Dropped"],
            [1 - dropout_probability - transfer_probability, transfer_probability, dropout_probability],
        )[0]
        dropout_date = None
        dropout_reason = None
        transfer_school_id = None
        if status == "Dropped":
            dropout_date = enrollment_date + timedelta(days=rng.randint(35, 150))
            dropout_reason = rng.choice(["Family duties", "Moved away", "Fees issue", "Work", "Health", "Unknown"])
        elif status == "Transferred":
            other_schools = [item["school_id"] for item in schools if item["school_id"] != school["school_id"]]
            transfer_school_id = rng.choice(other_schools)

        students.append(
            {
                "student_id": f"STU_{index:05d}",
                "school_id": school["school_id"],
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                "gender": rng.choice(gender_variants),
                "age": age,
                "date_of_birth": iso_day(date(2026 - age, rng.randint(1, 12), rng.randint(1, 28))),
                "class_level": rng.choice(["Form 1", "Form 2", "Form 3", "Form 4"]),
                "stream": rng.choice(["A", "B", "C", "D"]),
                "guardian_occupation": rng.choice(GUARDIAN_OCCUPATIONS),
                "household_size": rng.randint(3, 10),
                "has_phone_access": has_phone_access,
                "distance_to_school_km": distance,
                "transport_mode": rng.choices(
                    ["Walk", "Bicycle", "Bus", "Motorbike", "Family vehicle"],
                    [0.58, 0.14, 0.18, 0.07, 0.03],
                )[0],
                "disability_status": rng.choices(
                    ["None", "Visual impairment", "Hearing impairment", "Mobility limitation"],
                    [0.965, 0.012, 0.011, 0.012],
                )[0],
                "baseline_confidence_score": baseline_score,
                "baseline_risk_level": "High" if baseline_score < 42 or distance > 9 else "Medium" if baseline_score < 60 or distance > 5 else "Low",
                "enrollment_date": iso_day(enrollment_date),
                "status": status,
                "dropout_date": iso_day(dropout_date),
                "dropout_reason": dropout_reason,
                "transfer_school_id": transfer_school_id,
                "program_cohort": "2026-T2",
            }
        )

    students.append(
        {
            "student_id": "BAD_STUDENT_001",
            "school_id": "SCH_DOES_NOT_EXIST",
            "first_name": "Quality",
            "last_name": "Issue",
            "gender": "unknown",
            "age": 99,
            "date_of_birth": "1900-01-01",
            "class_level": "Form 9",
            "stream": "Z",
            "guardian_occupation": "Unknown",
            "household_size": 0,
            "has_phone_access": False,
            "distance_to_school_km": 99,
            "transport_mode": "Teleport",
            "disability_status": "None",
            "baseline_confidence_score": 120,
            "baseline_risk_level": "High",
            "enrollment_date": "2026-99-99",
            "status": "Active",
            "dropout_date": None,
            "dropout_reason": None,
            "transfer_school_id": None,
            "program_cohort": "2026-T2",
        }
    )
    return students


def generate_sessions(
    rng: random.Random,
    schools: list[dict[str, Any]],
    curriculum_modules: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    sessions = []
    start = date(2026, 5, 4)
    session_index = 1
    for school in schools:
        delivery_modifier = 0.12 if school["internet_available"] else 0.0
        delivery_modifier += 0.08 if school["electricity_available"] else -0.05
        delivery_modifier += -0.08 if school["implementation_status"] == "Needs Support" else 0.04
        for module in curriculum_modules:
            planned = start + timedelta(days=(module["week_number"] - 1) * 7 + rng.randint(0, 2))
            delivery_probability = clamp(0.82 + delivery_modifier - ((school["school_context_risk"] - 1) * 0.18), 0.55, 0.97)
            delivered = planned + timedelta(days=rng.randint(0, 6)) if rng.random() < delivery_probability else None
            quality_score = None
            duration_minutes = None
            if delivered:
                quality_score = round(clamp(rng.gauss(3.8, 0.7) + (0.25 if school["internet_available"] else -0.15), 1.0, 5.0), 1)
                duration_minutes = max(45, int(rng.gauss(module["expected_duration_minutes"], 14)))
            sessions.append(
                {
                    "session_id": f"SES_{session_index:05d}",
                    "school_id": school["school_id"],
                    "facilitator_id": school["facilitator_id"],
                    "module_id": module["module_id"],
                    "module_name": module["module_name"],
                    "competency_area": module["competency_area"],
                    "term": "Term 2",
                    "planned_date": iso_day(planned),
                    "delivered_date": iso_day(delivered),
                    "delivery_status": "Delivered" if delivered else "Planned",
                    "delivery_mode": rng.choices(["In-person", "Hybrid", "Catch-up"], [0.88, 0.06, 0.06])[0],
                    "duration_minutes": duration_minutes,
                    "delivery_quality_score": quality_score,
                    "materials_available": rng.random() < (0.91 if school["urban_rural"] == "Urban" else 0.76),
                }
            )
            session_index += 1
    return sessions


def generate_attendance(
    rng: random.Random,
    students: list[dict[str, Any]],
    sessions: list[dict[str, Any]],
    collectors: list[dict[str, Any]],
    devices: list[dict[str, Any]],
    schools: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    students_by_school: dict[str, list[dict[str, Any]]] = {}
    for student in students:
        if student.get("status") == "Active":
            students_by_school.setdefault(student["school_id"], []).append(student)

    collectors_by_district = {(item["assigned_region"], item["assigned_district"]): item for item in collectors}
    device_by_collector = {item["assigned_to"]: item for item in devices}
    school_lookup = {school["school_id"]: school for school in schools}

    attendance = []
    attendance_index = 1
    for session in sessions:
        if session["delivery_status"] != "Delivered":
            continue
        school = school_lookup[session["school_id"]]
        collector = collectors_by_district.get((school["region"], school["district"])) or collectors[0]
        device = device_by_collector.get(collector["collector_id"], devices[0])
        school_students = students_by_school.get(session["school_id"], [])
        sample_size = min(len(school_students), rng.randint(24, 42))
        for student in rng.sample(school_students, sample_size):
            distance_penalty = student["distance_to_school_km"] * 0.018
            rural_penalty = 0.045 if school["urban_rural"] == "Rural" else 0
            risk_penalty = {"Low": 0, "Medium": 0.045, "High": 0.09}[student["baseline_risk_level"]]
            attendance_probability = clamp(0.86 - distance_penalty - rural_penalty - risk_penalty, 0.42, 0.96)
            attended = rng.random() < attendance_probability
            minutes_late = 0
            arrival_status = "On time"
            if attended and rng.random() < clamp(0.12 + student["distance_to_school_km"] / 70, 0.1, 0.36):
                minutes_late = rng.randint(5, 45)
                arrival_status = "Late"
            upload_delay = rng.randint(0, 1)
            if device["connectivity_quality"] == "Poor":
                upload_delay = rng.randint(1, 8)
            elif device["connectivity_quality"] == "Intermittent":
                upload_delay = rng.randint(0, 4)
            recorded_at = datetime.fromisoformat(session["delivered_date"]).replace(tzinfo=timezone.utc) + timedelta(
                hours=rng.randint(2, 8),
                days=upload_delay,
            )
            attendance.append(
                {
                    "attendance_id": f"ATT_{attendance_index:06d}",
                    "student_id": student["student_id"],
                    "session_id": session["session_id"],
                    "school_id": session["school_id"],
                    "attendance_date": session["delivered_date"],
                    "attended": attended,
                    "arrival_status": arrival_status if attended else "Absent",
                    "minutes_late": minutes_late,
                    "absence_reason": None if attended else rng.choice(ABSENCE_REASONS),
                    "recorded_by": collector["collector_id"],
                    "source_device_id": device["device_id"],
                    "recorded_at": iso_dt(recorded_at),
                    "is_late_submission": upload_delay > 2,
                    "upload_delay_days": upload_delay,
                    "submission_channel": rng.choice(["ODK mobile", "CommCare mobile", "CSV upload"]),
                }
            )
            attendance_index += 1

    if attendance:
        duplicate = dict(attendance[0])
        duplicate["attendance_id"] = f"ATT_{attendance_index:06d}"
        attendance.append(duplicate)
        attendance_index += 1

    attendance.append(
        {
            "attendance_id": f"ATT_{attendance_index:06d}",
            "student_id": "",
            "session_id": sessions[0]["session_id"],
            "school_id": sessions[0]["school_id"],
            "attendance_date": sessions[0]["delivered_date"],
            "attended": True,
            "arrival_status": "On time",
            "minutes_late": 0,
            "absence_reason": None,
            "recorded_by": collectors[0]["collector_id"],
            "source_device_id": devices[0]["device_id"],
            "recorded_at": sessions[0]["delivered_date"],
            "is_late_submission": False,
            "upload_delay_days": 0,
            "submission_channel": "ODK mobile",
        }
    )
    return attendance


def generate_assessments(
    rng: random.Random,
    students: list[dict[str, Any]],
    collectors: list[dict[str, Any]],
    devices: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    assessments = []
    assessment_index = 1
    device_by_collector = {item["assigned_to"]: item for item in devices}
    for student in students:
        if not student["student_id"].startswith("STU_") or student["status"] != "Active":
            continue
        if rng.random() < 0.93:
            collector = rng.choice(collectors)
            device = device_by_collector.get(collector["collector_id"], devices[0])
            base = student["baseline_confidence_score"]
            pre_total = round(clamp(rng.gauss(base, 9), 0, 100), 1)
            pre_business = round(clamp(pre_total + rng.gauss(0, 8), 0, 100), 1)
            pre_finance = round(clamp(pre_total + rng.gauss(-2, 8), 0, 100), 1)
            pre_comm = round(clamp(pre_total + rng.gauss(1, 7), 0, 100), 1)
            pre_problem = round(clamp(pre_total + rng.gauss(-1, 8), 0, 100), 1)
            assessments.append(
                {
                    "assessment_id": f"ASM_{assessment_index:06d}",
                    "student_id": student["student_id"],
                    "school_id": student["school_id"],
                    "assessment_type": "Pre",
                    "term": "Term 2",
                    "score": pre_total,
                    "score_business": pre_business,
                    "score_financial_literacy": pre_finance,
                    "score_communication": pre_comm,
                    "score_problem_solving": pre_problem,
                    "max_score": 100,
                    "assessment_date": "2026-05-01",
                    "assessor_id": collector["collector_id"],
                    "source_device_id": device["device_id"],
                    "submission_source": rng.choice(["Tablet form", "Phone form", "Paper backfill"]),
                }
            )
            assessment_index += 1
            post_probability = 0.84
            if student["baseline_risk_level"] == "High":
                post_probability -= 0.12
            if rng.random() < post_probability:
                lift = rng.gauss(12, 7) + (4 if student["has_phone_access"] else 0)
                post_total = round(clamp(pre_total + lift, 0, 100), 1)
                assessments.append(
                    {
                        "assessment_id": f"ASM_{assessment_index:06d}",
                        "student_id": student["student_id"],
                        "school_id": student["school_id"],
                        "assessment_type": "Post",
                        "term": "Term 2",
                        "score": post_total,
                        "score_business": round(clamp(pre_business + lift + rng.gauss(1, 5), 0, 100), 1),
                        "score_financial_literacy": round(clamp(pre_finance + lift + rng.gauss(2, 5), 0, 100), 1),
                        "score_communication": round(clamp(pre_comm + lift + rng.gauss(0, 5), 0, 100), 1),
                        "score_problem_solving": round(clamp(pre_problem + lift + rng.gauss(1, 5), 0, 100), 1),
                        "max_score": 100,
                        "assessment_date": "2026-07-15",
                        "assessor_id": collector["collector_id"],
                        "source_device_id": device["device_id"],
                        "submission_source": rng.choice(["Tablet form", "Phone form", "Paper backfill"]),
                    }
                )
                assessment_index += 1

    assessments.append(
        {
            "assessment_id": f"ASM_{assessment_index:06d}",
            "student_id": students[0]["student_id"],
            "school_id": students[0]["school_id"],
            "assessment_type": "Post",
            "term": "Term 2",
            "score": 132,
            "score_business": 132,
            "score_financial_literacy": 132,
            "score_communication": 132,
            "score_problem_solving": 132,
            "max_score": 100,
            "assessment_date": "2026-07-15",
            "assessor_id": collectors[0]["collector_id"],
            "source_device_id": devices[0]["device_id"],
            "submission_source": "Paper backfill",
        }
    )
    return assessments


def generate_facilitator_visits(
    rng: random.Random,
    schools: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    visits = []
    visit_index = 1
    for school in schools:
        for month_offset in range(3):
            planned = date(2026, 5, 10) + timedelta(days=month_offset * 30 + rng.randint(0, 5))
            visit_probability = clamp(0.84 - ((school["school_context_risk"] - 1) * 0.2), 0.62, 0.96)
            completed = planned + timedelta(days=rng.randint(0, 5)) if rng.random() < visit_probability else None
            issues_found = []
            if school["implementation_status"] == "Needs Support" or rng.random() < 0.18:
                issues_found.append(rng.choice(["Low attendance", "Materials missing", "Late data upload", "Session backlog"]))
            visits.append(
                {
                    "visit_id": f"VIS_{visit_index:05d}",
                    "school_id": school["school_id"],
                    "facilitator_id": school["facilitator_id"],
                    "visit_type": rng.choice(["Routine coaching", "Data verification", "Remedial support"]),
                    "planned_date": iso_day(planned),
                    "completed_date": iso_day(completed),
                    "duration_minutes": rng.randint(45, 160) if completed else None,
                    "visit_status": "Completed" if completed else "Missed",
                    "issues_found": issues_found,
                    "coaching_score": round(clamp(rng.gauss(3.7, 0.8), 1, 5), 1) if completed else None,
                    "follow_up_required": bool(issues_found),
                    "follow_up_due_date": iso_day(planned + timedelta(days=14)) if issues_found else None,
                    "notes": rng.choice(["", "Teacher requested extra materials.", "Attendance register needs review.", "Student group work was strong."]),
                }
            )
            visit_index += 1
    return visits


def generate_student_surveys(
    rng: random.Random,
    students: list[dict[str, Any]],
    collectors: list[dict[str, Any]],
    devices: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    surveys = []
    survey_index = 1
    device_by_collector = {item["assigned_to"]: item for item in devices}
    for student in students:
        if not student["student_id"].startswith("STU_") or student["status"] != "Active":
            continue
        if rng.random() > 0.64:
            continue
        collector = rng.choice(collectors)
        device = device_by_collector.get(collector["collector_id"], devices[0])
        base = 3.1 if student["baseline_risk_level"] == "High" else 3.7 if student["baseline_risk_level"] == "Medium" else 4.1
        surveys.append(
            {
                "survey_id": f"SRV_{survey_index:06d}",
                "student_id": student["student_id"],
                "school_id": student["school_id"],
                "term": "Term 2",
                "survey_date": iso_day(date(2026, 7, 12) + timedelta(days=rng.randint(0, 10))),
                "confidence_score": round(clamp(rng.gauss(base + 0.4, 0.7), 1, 5), 1),
                "entrepreneurship_interest": round(clamp(rng.gauss(base + 0.3, 0.8), 1, 5), 1),
                "financial_confidence": round(clamp(rng.gauss(base + 0.2, 0.8), 1, 5), 1),
                "teamwork_confidence": round(clamp(rng.gauss(base + 0.5, 0.7), 1, 5), 1),
                "satisfaction_score": round(clamp(rng.gauss(base + 0.6, 0.6), 1, 5), 1),
                "would_recommend_program": rng.random() < 0.86,
                "open_feedback": rng.choice(FEEDBACK_SNIPPETS),
                "recorded_by": collector["collector_id"],
                "source_device_id": device["device_id"],
            }
        )
        survey_index += 1
    return surveys


def generate_program_targets(schools: list[dict[str, Any]]) -> list[dict[str, Any]]:
    targets_by_district: dict[tuple[str, str], dict[str, Any]] = {}
    for school in schools:
        key = (school["region"], school["district"])
        target = targets_by_district.setdefault(
            key,
            {
                "target_id": f"TGT_{len(targets_by_district) + 1:03d}",
                "region": school["region"],
                "district": school["district"],
                "term": "Term 2",
                "target_students": 0,
                "target_active_students": 0,
                "target_sessions": 0,
                "target_attendance_rate": 0.80 if school["urban_rural"] == "Urban" else 0.74,
                "target_assessment_completion_rate": 0.78,
                "target_visit_completion_rate": 0.88,
            },
        )
        target["target_students"] += 35
        target["target_active_students"] += 31
        target["target_sessions"] += len(CURRICULUM_BLUEPRINT)
    return list(targets_by_district.values())


def generate_source_uploads(
    rng: random.Random,
    collectors: list[dict[str, Any]],
    devices: list[dict[str, Any]],
    attendance: list[dict[str, Any]],
    assessments: list[dict[str, Any]],
    surveys: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    datasets = [
        ("attendance", attendance, "attendance_term2_weekly.csv"),
        ("assessments", assessments, "assessment_term2_scores.csv"),
        ("student_surveys", surveys, "student_survey_term2.json"),
    ]
    uploads = []
    index = 1
    for source_name, rows, filename in datasets:
        chunks = max(3, min(8, len(rows) // 700 + 3))
        for chunk in range(chunks):
            collector = rng.choice(collectors)
            device = rng.choice([item for item in devices if item["assigned_to"] == collector["collector_id"]] or devices)
            expected = max(40, len(rows) // chunks + rng.randint(-20, 35))
            invalid = rng.randint(0, max(2, expected // 35))
            duplicate = rng.randint(0, max(1, expected // 80))
            loaded = max(0, expected - rng.randint(0, 6))
            uploaded_at = datetime(2026, 7, 5 + chunk * 2, rng.randint(7, 20), rng.randint(0, 59), tzinfo=timezone.utc)
            if device["connectivity_quality"] == "Poor":
                uploaded_at += timedelta(days=rng.randint(2, 5))
            uploads.append(
                {
                    "source_upload_id": f"UPL_{index:05d}",
                    "source_name": source_name,
                    "source_file": f"{filename.replace('.', f'_{chunk + 1:02d}.')}",
                    "uploaded_by": collector["collector_id"],
                    "uploaded_at": iso_dt(uploaded_at),
                    "expected_records": expected,
                    "loaded_records": loaded,
                    "valid_records": max(0, loaded - invalid - duplicate),
                    "invalid_records": invalid,
                    "duplicate_records": duplicate,
                    "latest_record_date": "2026-07-15",
                    "pipeline_status": "Loaded with warnings" if invalid or duplicate else "Loaded",
                    "source_device_id": device["device_id"],
                    "connectivity_quality": device["connectivity_quality"],
                }
            )
            index += 1
    return uploads


def generate_interventions(
    rng: random.Random,
    schools: list[dict[str, Any]],
    students: list[dict[str, Any]],
    facilitator_visits: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    interventions = []
    index = 1
    students_by_school: dict[str, list[dict[str, Any]]] = {}
    for student in students:
        if student.get("status") == "Active":
            students_by_school.setdefault(student["school_id"], []).append(student)

    for school in schools:
        school_students = students_by_school.get(school["school_id"], [])
        high_risk_students = [student for student in school_students if student["baseline_risk_level"] == "High"]
        if school["implementation_status"] == "Needs Support" or high_risk_students:
            for _ in range(min(3, max(1, len(high_risk_students) // 10))):
                student = rng.choice(high_risk_students) if high_risk_students and rng.random() < 0.75 else None
                opened = date(2026, 6, 1) + timedelta(days=rng.randint(0, 45))
                closed = opened + timedelta(days=rng.randint(7, 30)) if rng.random() < 0.55 else None
                interventions.append(
                    {
                        "intervention_id": f"INT_{index:05d}",
                        "school_id": school["school_id"],
                        "student_id": student["student_id"] if student else None,
                        "intervention_type": rng.choice(
                            [
                                "Low attendance follow-up",
                                "Missing post-assessment",
                                "School delivery support",
                                "Data correction request",
                                "Facilitator visit follow-up",
                            ]
                        ),
                        "trigger_reason": "High baseline risk" if student else rng.choice(["Session backlog", "Late upload", "Low attendance"]),
                        "assigned_to": school["facilitator_id"],
                        "opened_date": iso_day(opened),
                        "due_date": iso_day(opened + timedelta(days=14)),
                        "closed_date": iso_day(closed),
                        "status": "Closed" if closed else rng.choice(["Open", "In Progress", "Overdue"]),
                        "outcome": rng.choice(["Resolved", "Monitoring", "Escalated", "Pending school response"]) if closed else None,
                        "priority": "High" if student and student["distance_to_school_km"] > 8 else rng.choice(["Medium", "High", "Low"]),
                    }
                )
                index += 1

    for visit in facilitator_visits:
        if visit["follow_up_required"] and rng.random() < 0.62:
            opened = datetime.fromisoformat(visit["planned_date"]).date()
            interventions.append(
                {
                    "intervention_id": f"INT_{index:05d}",
                    "school_id": visit["school_id"],
                    "student_id": None,
                    "intervention_type": "Facilitator visit follow-up",
                    "trigger_reason": "; ".join(visit["issues_found"]),
                    "assigned_to": visit["facilitator_id"],
                    "opened_date": iso_day(opened),
                    "due_date": iso_day(opened + timedelta(days=14)),
                    "closed_date": None,
                    "status": rng.choice(["Open", "In Progress"]),
                    "outcome": None,
                    "priority": "Medium",
                }
            )
            index += 1
    return interventions


def generate_all() -> dict[str, Any]:
    settings = get_settings()
    fake = Faker()
    Faker.seed(settings.data_seed)
    rng = random.Random(settings.data_seed)

    curriculum_modules = generate_curriculum_modules()
    schools = generate_schools(fake, rng)
    facilitators = generate_facilitators(fake, rng, schools)
    assign_facilitators(rng, schools, facilitators)
    data_collectors = generate_data_collectors(fake, rng, facilitators)
    field_devices = generate_field_devices(rng, data_collectors)
    students = generate_students(fake, rng, schools)
    sessions = generate_sessions(rng, schools, curriculum_modules)
    attendance = generate_attendance(rng, students, sessions, data_collectors, field_devices, schools)
    assessments = generate_assessments(rng, students, data_collectors, field_devices)
    facilitator_visits = generate_facilitator_visits(rng, schools)
    student_surveys = generate_student_surveys(rng, students, data_collectors, field_devices)
    program_targets = generate_program_targets(schools)
    interventions = generate_interventions(rng, schools, students, facilitator_visits)
    source_uploads = generate_source_uploads(rng, data_collectors, field_devices, attendance, assessments, student_surveys)

    files = {
        "schools.json": schools,
        "facilitators.json": facilitators,
        "data_collectors.json": data_collectors,
        "field_devices.json": field_devices,
        "curriculum_modules.json": curriculum_modules,
        "students.json": students,
        "sessions.json": sessions,
        "attendance.json": attendance,
        "assessments.json": assessments,
        "facilitator_visits.json": facilitator_visits,
        "student_surveys.json": student_surveys,
        "program_targets.json": program_targets,
        "source_uploads.json": source_uploads,
        "interventions.json": interventions,
    }

    for filename, rows in files.items():
        write_json(DATA_DIR / filename, rows)

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "seed": settings.data_seed,
        "files": {filename: len(rows) for filename, rows in files.items()},
    }
    write_json(DATA_DIR / "manifest.json", [manifest])
    print(f"Generated enhanced synthetic data in {DATA_DIR}")
    return {
        "generated_at": manifest["generated_at"],
        "files": manifest["files"],
        "total_records": sum(manifest["files"].values()),
    }


if __name__ == "__main__":
    generate_all()
