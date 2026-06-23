from __future__ import annotations

from src.db import get_database


def build_school_performance_mart() -> None:
    db = get_database()
    db.schools.aggregate(
        [
            {
                "$lookup": {
                    "from": "students",
                    "localField": "school_id",
                    "foreignField": "school_id",
                    "as": "students",
                }
            },
            {
                "$lookup": {
                    "from": "sessions",
                    "localField": "school_id",
                    "foreignField": "school_id",
                    "as": "sessions",
                }
            },
            {
                "$lookup": {
                    "from": "facilitator_visits",
                    "localField": "school_id",
                    "foreignField": "school_id",
                    "as": "visits",
                }
            },
            {
                "$lookup": {
                    "from": "quality_issues",
                    "localField": "school_id",
                    "foreignField": "school_id",
                    "as": "quality_issues",
                }
            },
            {
                "$lookup": {
                    "from": "student_surveys",
                    "localField": "school_id",
                    "foreignField": "school_id",
                    "as": "student_surveys",
                }
            },
            {
                "$lookup": {
                    "from": "interventions",
                    "localField": "school_id",
                    "foreignField": "school_id",
                    "as": "interventions",
                }
            },
            {
                "$set": {
                    "student_ids": {
                        "$map": {
                            "input": "$students",
                            "as": "student",
                            "in": "$$student.student_id",
                        }
                    },
                    "session_ids": {
                        "$map": {
                            "input": "$sessions",
                            "as": "session",
                            "in": "$$session.session_id",
                        }
                    },
                }
            },
            {
                "$lookup": {
                    "from": "attendance",
                    "let": {"session_ids": "$session_ids"},
                    "pipeline": [
                        {"$match": {"$expr": {"$in": ["$session_id", "$$session_ids"]}}},
                    ],
                    "as": "attendance",
                }
            },
            {
                "$lookup": {
                    "from": "assessments",
                    "let": {"student_ids": "$student_ids"},
                    "pipeline": [
                        {"$match": {"$expr": {"$in": ["$student_id", "$$student_ids"]}}},
                    ],
                    "as": "assessments",
                }
            },
            {
                "$set": {
                    "active_students_docs": {
                        "$filter": {
                            "input": "$students",
                            "as": "student",
                            "cond": {"$eq": ["$$student.status", "Active"]},
                        }
                    },
                    "delivered_sessions_docs": {
                        "$filter": {
                            "input": "$sessions",
                            "as": "session",
                            "cond": {"$eq": ["$$session.delivery_status", "Delivered"]},
                        }
                    },
                    "attended_docs": {
                        "$filter": {
                            "input": "$attendance",
                            "as": "att",
                            "cond": {"$eq": ["$$att.attended", True]},
                        }
                    },
                    "late_submission_docs": {
                        "$filter": {
                            "input": "$attendance",
                            "as": "att",
                            "cond": {"$eq": ["$$att.is_late_submission", True]},
                        }
                    },
                    "completed_visit_docs": {
                        "$filter": {
                            "input": "$visits",
                            "as": "visit",
                            "cond": {"$eq": ["$$visit.visit_status", "Completed"]},
                        }
                    },
                    "pre_student_ids": {
                        "$setUnion": [
                            {
                                "$map": {
                                    "input": {
                                        "$filter": {
                                            "input": "$assessments",
                                            "as": "assessment",
                                            "cond": {"$eq": ["$$assessment.assessment_type", "Pre"]},
                                        }
                                    },
                                    "as": "assessment",
                                    "in": "$$assessment.student_id",
                                }
                            }
                        ]
                    },
                    "post_student_ids": {
                        "$setUnion": [
                            {
                                "$map": {
                                    "input": {
                                        "$filter": {
                                            "input": "$assessments",
                                            "as": "assessment",
                                            "cond": {"$eq": ["$$assessment.assessment_type", "Post"]},
                                        }
                                    },
                                    "as": "assessment",
                                    "in": "$$assessment.student_id",
                                }
                            }
                        ]
                    },
                    "high_risk_student_docs": {
                        "$filter": {
                            "input": "$students",
                            "as": "student",
                            "cond": {"$eq": ["$$student.baseline_risk_level", "High"]},
                        }
                    },
                    "open_intervention_docs": {
                        "$filter": {
                            "input": "$interventions",
                            "as": "intervention",
                            "cond": {"$in": ["$$intervention.status", ["Open", "In Progress", "Overdue"]]},
                        }
                    },
                }
            },
            {
                "$set": {
                    "active_students": {"$size": "$active_students_docs"},
                    "sessions_planned": {"$size": "$sessions"},
                    "sessions_delivered": {"$size": "$delivered_sessions_docs"},
                    "attendance_records": {"$size": "$attendance"},
                    "attended_records": {"$size": "$attended_docs"},
                    "late_submission_records": {"$size": "$late_submission_docs"},
                    "visits_planned": {"$size": "$visits"},
                    "visits_completed": {"$size": "$completed_visit_docs"},
                    "assessment_completed_students": {
                        "$size": {"$setIntersection": ["$pre_student_ids", "$post_student_ids"]}
                    },
                    "data_quality_issues": {"$size": "$quality_issues"},
                    "high_risk_students": {"$size": "$high_risk_student_docs"},
                    "open_interventions": {"$size": "$open_intervention_docs"},
                    "avg_distance_to_school_km": {"$avg": "$students.distance_to_school_km"},
                    "avg_delivery_quality_score": {"$avg": "$delivered_sessions_docs.delivery_quality_score"},
                    "avg_satisfaction_score": {"$avg": "$student_surveys.satisfaction_score"},
                }
            },
            {
                "$set": {
                    "session_delivery_rate": {
                        "$cond": [
                            {"$gt": ["$sessions_planned", 0]},
                            {"$divide": ["$sessions_delivered", "$sessions_planned"]},
                            None,
                        ]
                    },
                    "attendance_rate": {
                        "$cond": [
                            {"$gt": ["$attendance_records", 0]},
                            {"$divide": ["$attended_records", "$attendance_records"]},
                            None,
                        ]
                    },
                    "late_submission_rate": {
                        "$cond": [
                            {"$gt": ["$attendance_records", 0]},
                            {"$divide": ["$late_submission_records", "$attendance_records"]},
                            None,
                        ]
                    },
                    "facilitator_visit_completion_rate": {
                        "$cond": [
                            {"$gt": ["$visits_planned", 0]},
                            {"$divide": ["$visits_completed", "$visits_planned"]},
                            None,
                        ]
                    },
                    "assessment_completion_rate": {
                        "$cond": [
                            {"$gt": ["$active_students", 0]},
                            {"$divide": ["$assessment_completed_students", "$active_students"]},
                            None,
                        ]
                    },
                }
            },
            {
                "$set": {
                    "risk_status": {
                        "$switch": {
                            "branches": [
                                {
                                    "case": {
                                        "$or": [
                                            {"$lt": ["$attendance_rate", 0.68]},
                                            {"$lt": ["$session_delivery_rate", 0.72]},
                                        ]
                                    },
                                    "then": "High Risk",
                                },
                                {
                                    "case": {
                                        "$or": [
                                            {"$lt": ["$attendance_rate", 0.8]},
                                            {"$lt": ["$session_delivery_rate", 0.85]},
                                        ]
                                    },
                                    "then": "Watch",
                                },
                            ],
                            "default": "On Track",
                        }
                    }
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "school_id": 1,
                    "school_name": 1,
                    "region": 1,
                    "district": 1,
                    "ward": 1,
                    "street_address": 1,
                    "latitude": 1,
                    "longitude": 1,
                    "location": 1,
                    "school_type": 1,
                    "urban_rural": 1,
                    "ownership": 1,
                    "electricity_available": 1,
                    "internet_available": 1,
                    "water_access": 1,
                    "term": "Term 2",
                    "active_students": 1,
                    "high_risk_students": 1,
                    "sessions_planned": 1,
                    "sessions_delivered": 1,
                    "session_delivery_rate": {"$round": ["$session_delivery_rate", 3]},
                    "attendance_rate": {"$round": ["$attendance_rate", 3]},
                    "late_submission_rate": {"$round": ["$late_submission_rate", 3]},
                    "assessment_completion_rate": {"$round": ["$assessment_completion_rate", 3]},
                    "facilitator_visit_completion_rate": {
                        "$round": ["$facilitator_visit_completion_rate", 3]
                    },
                    "avg_distance_to_school_km": {"$round": ["$avg_distance_to_school_km", 2]},
                    "avg_delivery_quality_score": {"$round": ["$avg_delivery_quality_score", 2]},
                    "avg_satisfaction_score": {"$round": ["$avg_satisfaction_score", 2]},
                    "open_interventions": 1,
                    "data_quality_issues": 1,
                    "risk_status": 1,
                }
            },
            {
                "$merge": {
                    "into": "mart_school_performance",
                    "on": "school_id",
                    "whenMatched": "replace",
                    "whenNotMatched": "insert",
                }
            },
        ],
        allowDiskUse=True,
    )


def build_regional_summary_mart() -> None:
    db = get_database()
    db.mart_school_performance.aggregate(
        [
            {
                "$group": {
                    "_id": {"region": "$region", "district": "$district"},
                    "schools": {"$sum": 1},
                    "active_students": {"$sum": "$active_students"},
                    "high_risk_students": {"$sum": "$high_risk_students"},
                    "avg_attendance_rate": {"$avg": "$attendance_rate"},
                    "avg_session_delivery_rate": {"$avg": "$session_delivery_rate"},
                    "avg_assessment_completion_rate": {"$avg": "$assessment_completion_rate"},
                    "avg_late_submission_rate": {"$avg": "$late_submission_rate"},
                    "avg_delivery_quality_score": {"$avg": "$avg_delivery_quality_score"},
                    "avg_satisfaction_score": {"$avg": "$avg_satisfaction_score"},
                    "avg_distance_to_school_km": {"$avg": "$avg_distance_to_school_km"},
                    "open_interventions": {"$sum": "$open_interventions"},
                    "at_risk_schools": {
                        "$sum": {"$cond": [{"$ne": ["$risk_status", "On Track"]}, 1, 0]}
                    },
                    "data_quality_issues": {"$sum": "$data_quality_issues"},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "region": "$_id.region",
                    "district": "$_id.district",
                    "schools": 1,
                    "active_students": 1,
                    "high_risk_students": 1,
                    "avg_attendance_rate": {"$round": ["$avg_attendance_rate", 3]},
                    "avg_session_delivery_rate": {"$round": ["$avg_session_delivery_rate", 3]},
                    "avg_assessment_completion_rate": {
                        "$round": ["$avg_assessment_completion_rate", 3]
                    },
                    "avg_late_submission_rate": {"$round": ["$avg_late_submission_rate", 3]},
                    "avg_delivery_quality_score": {"$round": ["$avg_delivery_quality_score", 2]},
                    "avg_satisfaction_score": {"$round": ["$avg_satisfaction_score", 2]},
                    "avg_distance_to_school_km": {"$round": ["$avg_distance_to_school_km", 2]},
                    "open_interventions": 1,
                    "at_risk_schools": 1,
                    "data_quality_issues": 1,
                }
            },
            {
                "$merge": {
                    "into": "mart_regional_summary",
                    "on": ["region", "district"],
                    "whenMatched": "replace",
                    "whenNotMatched": "insert",
                }
            },
        ]
    )


def build_term2_overview_mart() -> None:
    db = get_database()
    db.mart_school_performance.aggregate(
        [
            {
                "$group": {
                    "_id": "$term",
                    "schools": {"$sum": 1},
                    "active_students": {"$sum": "$active_students"},
                    "high_risk_students": {"$sum": "$high_risk_students"},
                    "avg_attendance_rate": {"$avg": "$attendance_rate"},
                    "avg_session_delivery_rate": {"$avg": "$session_delivery_rate"},
                    "avg_assessment_completion_rate": {"$avg": "$assessment_completion_rate"},
                    "avg_late_submission_rate": {"$avg": "$late_submission_rate"},
                    "avg_delivery_quality_score": {"$avg": "$avg_delivery_quality_score"},
                    "avg_satisfaction_score": {"$avg": "$avg_satisfaction_score"},
                    "avg_distance_to_school_km": {"$avg": "$avg_distance_to_school_km"},
                    "avg_facilitator_visit_completion_rate": {
                        "$avg": "$facilitator_visit_completion_rate"
                    },
                    "open_interventions": {"$sum": "$open_interventions"},
                    "at_risk_schools": {
                        "$sum": {"$cond": [{"$ne": ["$risk_status", "On Track"]}, 1, 0]}
                    },
                    "data_quality_issues": {"$sum": "$data_quality_issues"},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "term": "$_id",
                    "schools": 1,
                    "active_students": 1,
                    "high_risk_students": 1,
                    "avg_attendance_rate": {"$round": ["$avg_attendance_rate", 3]},
                    "avg_session_delivery_rate": {"$round": ["$avg_session_delivery_rate", 3]},
                    "avg_assessment_completion_rate": {
                        "$round": ["$avg_assessment_completion_rate", 3]
                    },
                    "avg_late_submission_rate": {"$round": ["$avg_late_submission_rate", 3]},
                    "avg_delivery_quality_score": {"$round": ["$avg_delivery_quality_score", 2]},
                    "avg_satisfaction_score": {"$round": ["$avg_satisfaction_score", 2]},
                    "avg_distance_to_school_km": {"$round": ["$avg_distance_to_school_km", 2]},
                    "avg_facilitator_visit_completion_rate": {
                        "$round": ["$avg_facilitator_visit_completion_rate", 3]
                    },
                    "open_interventions": 1,
                    "at_risk_schools": 1,
                    "data_quality_issues": 1,
                }
            },
            {
                "$merge": {
                    "into": "mart_term2_overview",
                    "on": "term",
                    "whenMatched": "replace",
                    "whenNotMatched": "insert",
                }
            },
        ]
    )


def build_data_quality_mart() -> None:
    db = get_database()
    db.quality_issues.aggregate(
        [
            {
                "$group": {
                    "_id": {
                        "collection": "$collection",
                        "issue_type": "$issue_type",
                        "severity": "$severity",
                    },
                    "issue_count": {"$sum": 1},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "collection": "$_id.collection",
                    "issue_type": "$_id.issue_type",
                    "severity": "$_id.severity",
                    "issue_count": 1,
                }
            },
            {
                "$merge": {
                    "into": "mart_data_quality",
                    "on": ["collection", "issue_type", "severity"],
                    "whenMatched": "replace",
                    "whenNotMatched": "insert",
                }
            },
        ]
    )


def build_all_marts() -> dict[str, object]:
    db = get_database()
    db.mart_school_performance.delete_many({})
    db.mart_regional_summary.delete_many({})
    db.mart_term2_overview.delete_many({})
    db.mart_data_quality.delete_many({})
    build_school_performance_mart()
    build_regional_summary_mart()
    build_term2_overview_mart()
    build_data_quality_mart()
    print("Built dashboard mart collections")
    mart_collections = [
        "mart_school_performance",
        "mart_regional_summary",
        "mart_term2_overview",
        "mart_data_quality",
    ]
    return {
        "mart_counts": {
            collection_name: db[collection_name].count_documents({})
            for collection_name in mart_collections
        },
        "marts_built": len(mart_collections),
    }


if __name__ == "__main__":
    build_all_marts()
