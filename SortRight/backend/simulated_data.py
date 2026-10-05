"""
SortRight - Simulated Analytics Data Generator
Simulated demo data for prototype staff portal. Not real scan data.
"""

from typing import Dict, Any, List

DISCLAIMER_NOTICE = "Simulated demo data. Not real scan data."
PRIVACY_NOTICE = "Area-level aggregates only. No images or personal identity stored. Areas with very few scans are suppressed."

def get_municipality_analytics(days: int = 30) -> Dict[str, Any]:
    """
    Returns simulated municipality planning data for Coimbatore city.
    """
    multiplier = days / 30.0

    return {
        "disclaimer": DISCLAIMER_NOTICE,
        "privacy_notice": PRIVACY_NOTICE,
        "period_days": days,
        "kpi": {
            "total_scans": int(124850 * multiplier),
            "scans_growth_pct": 18.2,
            "segregation_accuracy_pct": 78.4,
            "accuracy_target_pct": 80.0,
            "contamination_rate_pct": 14.2,
            "contamination_reduction_pct": 3.1,
            "ewaste_routed_kg": int(3180 * multiplier),
            "ewaste_growth_pct": 12.5
        },
        "waste_mix": [
            {"category": "Dry Recyclables", "share_pct": 42.0, "color": "#16a34a"},
            {"category": "Organic (Wet)", "share_pct": 38.0, "color": "#92400e"},
            {"category": "Reject / General Dry", "share_pct": 14.0, "color": "#64748b"},
            {"category": "Special / E-Waste", "share_pct": 6.0, "color": "#dc2626"}
        ],
        "ward_table": [
            {
                "ward_id": "W-01",
                "ward_name": "RS Puram",
                "scans": int(18400 * multiplier),
                "recyclable_pct": 82.5,
                "organic_pct": 12.0,
                "contamination_pct": 5.5,
                "ewaste_kg": int(620 * multiplier),
                "status": "Good"
            },
            {
                "ward_id": "W-02",
                "ward_name": "Gandhipuram",
                "scans": int(26100 * multiplier),
                "recyclable_pct": 64.2,
                "organic_pct": 21.0,
                "contamination_pct": 28.6,
                "ewaste_kg": int(780 * multiplier),
                "status": "Action Required"
            },
            {
                "ward_id": "W-03",
                "ward_name": "Peelamedu",
                "scans": int(21800 * multiplier),
                "recyclable_pct": 73.1,
                "organic_pct": 24.5,
                "contamination_pct": 18.2,
                "ewaste_kg": int(540 * multiplier),
                "status": "Moderate"
            },
            {
                "ward_id": "W-04",
                "ward_name": "Singanallur",
                "scans": int(29400 * multiplier),
                "recyclable_pct": 61.8,
                "organic_pct": 29.2,
                "contamination_pct": 24.1,
                "ewaste_kg": int(810 * multiplier),
                "status": "Action Required"
            },
            {
                "ward_id": "W-05",
                "ward_name": "Saibaba Colony",
                "scans": int(16200 * multiplier),
                "recyclable_pct": 84.6,
                "organic_pct": 10.2,
                "contamination_pct": 9.8,
                "ewaste_kg": int(430 * multiplier),
                "status": "Good"
            }
        ],
        "planning_recommendations": [
            {
                "priority": "High",
                "target_ward": "Gandhipuram (Ward 02)",
                "issue": "High food-packaging contamination in dry recycling stream (28.6%).",
                "recommended_action": "Deploy targeted household door-to-door awareness stickers on rinsing takeout containers and grease contamination."
            },
            {
                "priority": "High",
                "target_ward": "Singanallur (Ward 04)",
                "issue": "Surge in dry plastic volume exceeding current bi-weekly collection capacity.",
                "recommended_action": "Schedule an additional Wednesday afternoon dry-waste collection vehicle to prevent bin overflows."
            },
            {
                "priority": "Medium",
                "target_ward": "Peelamedu (Ward 03)",
                "issue": "E-waste scans increased by 22% near university and tech hub clusters.",
                "recommended_action": "Install 2 additional dedicated e-waste collection kiosks at Avinashi Road public junctions."
            }
        ],
        "ewaste_trend": {
            "labels": ["Oct", "Nov", "Dec", "Jan", "Feb", "Mar"],
            "values_kg": [320, 410, 390, 520, 680, 840]
        }
    }

def get_recycler_analytics(days: int = 30) -> Dict[str, Any]:
    """
    Returns simulated material availability and recovery stream data for recycling aggregators.
    """
    multiplier = days / 30.0

    return {
        "disclaimer": DISCLAIMER_NOTICE,
        "privacy_notice": PRIVACY_NOTICE,
        "estimation_methodology": "Quantities are estimated based on simulated citizen scan frequency, item standard tare weights, and historical recovery yield rates.",
        "period_days": days,
        "material_availability": [
            {
                "material_type": "PET Plastic (#1)",
                "estimated_metric_tons": round(14.8 * multiplier, 1),
                "quality_grade": "Grade A (Clean Clear)",
                "top_origin_wards": ["RS Puram", "Saibaba Colony"],
                "price_trend": "+4.2% / ton"
            },
            {
                "material_type": "Corrugated Cardboard",
                "estimated_metric_tons": round(28.4 * multiplier, 1),
                "quality_grade": "Grade B (Mixed Packaging)",
                "top_origin_wards": ["Gandhipuram", "Singanallur"],
                "price_trend": "+1.8% / ton"
            },
            {
                "material_type": "Glass Containers",
                "estimated_metric_tons": round(9.2 * multiplier, 1),
                "quality_grade": "Mixed Cullet",
                "top_origin_wards": ["Peelamedu", "RS Puram"],
                "price_trend": "Stable"
            },
            {
                "material_type": "Aluminum Beverage Cans",
                "estimated_metric_tons": round(4.6 * multiplier, 1),
                "quality_grade": "High Purity UBC",
                "top_origin_wards": ["Gandhipuram", "Peelamedu"],
                "price_trend": "+6.5% / ton"
            },
            {
                "material_type": "E-Waste & Small Appliances",
                "estimated_metric_tons": round(3.2 * multiplier, 1),
                "quality_grade": "Mixed IT & Domestic Cells",
                "top_origin_wards": ["Peelamedu", "Singanallur"],
                "price_trend": "High Value"
            }
        ],
        "supply_trend": {
            "labels": ["Oct", "Nov", "Dec", "Jan", "Feb", "Mar"],
            "datasets": [
                {"label": "Cardboard (Tons)", "data": [18, 21, 24, 25, 27, 28]},
                {"label": "PET Plastic (Tons)", "data": [9, 10, 11, 12, 14, 15]}
            ]
        },
        "pickup_suggestions": [
            {
                "facility_name": "Coimbatore North Material Recovery Hub",
                "location": "Mettupalayam Road Zone",
                "available_batch": "4.2 Tons Baler-Ready PET",
                "optimal_pickup_window": "Mon & Thu 09:00 - 12:00"
            },
            {
                "facility_name": "Singanallur Secondary Segregation Shed",
                "location": "Trichy Road Depot",
                "available_batch": "7.8 Tons Compacted Cardboard",
                "optimal_pickup_window": "Tue & Fri 14:00 - 17:00"
            }
        ],
        "facilities": [
            {"name": "Central Material Recovery Facility", "type": "MRF / Baling", "capacity_tpd": 30, "status": "Operational"},
            {"name": "Peelamedu E-Waste Aggregation Point", "type": "Special Collection Hub", "capacity_tpd": 5, "status": "Operational"},
            {"name": "Ukkadam Organic Composting Yard", "type": "Aerobic Windrow", "capacity_tpd": 50, "status": "Operational"}
        ]
    }
