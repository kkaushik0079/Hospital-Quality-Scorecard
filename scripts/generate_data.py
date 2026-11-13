"""
Generate the synthetic dataset for the Hospital Quality Scorecard.

All data is SYNTHETIC. Hospital names are fictional. Measure definitions are
modeled on public CMS quality programs (Hospital Readmissions Reduction Program,
HCAHPS, OP-18b ED throughput, SEP-1 sepsis bundle, NHSN CLABSI SIR), but no
values come from CMS or from any real hospital.

Usage:
    python scripts/generate_data.py
Outputs:
    data/hospitals.csv           one row per hospital (12-month measures)
    data/monthly_readmissions.csv  monthly readmission counts by hospital and condition
    data/dashboard_data.json     the same data, shaped for index.html
"""
import csv
import json
import random
from pathlib import Path

random.seed(2026)
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

HOSPITALS = [
    ("H01", "Meridian North Medical Center", "North", 420),
    ("H02", "Meridian Lakeside Hospital", "North", 210),
    ("H03", "Meridian Ridgeview Hospital", "North", 160),
    ("H04", "Meridian Central Regional", "Central", 510),
    ("H05", "Meridian Riverside Hospital", "Central", 240),
    ("H06", "Meridian Parkway Hospital", "Central", 180),
    ("H07", "Meridian Westbrook Hospital", "Central", 130),
    ("H08", "Meridian South Medical Center", "South", 380),
    ("H09", "Meridian Harbor Hospital", "South", 220),
    ("H10", "Meridian Pinecrest Hospital", "South", 150),
]
CONDITIONS = {"AMI": 0.135, "HF": 0.205, "PN": 0.165, "COPD": 0.185}
MONTHS = ["2025-11", "2025-12", "2026-01", "2026-02", "2026-03", "2026-04",
          "2026-05", "2026-06", "2026-07", "2026-08", "2026-09", "2026-10"]
REGION_BIAS = {"North": -0.008, "Central": 0.004, "South": 0.012}

monthly = []
for hid, name, region, beds in HOSPITALS:
    hosp_bias = random.uniform(-0.02, 0.02) + REGION_BIAS[region]
    for i, month in enumerate(MONTHS):
        improvement = -0.0012 * i  # gradual improvement over the year
        season = 0.01 if month.endswith(("-12", "-01", "-02")) else 0.0
        for cond, base in CONDITIONS.items():
            discharges = max(8, int(beds * {"AMI": 0.05, "HF": 0.09, "PN": 0.07, "COPD": 0.06}[cond] * random.uniform(0.85, 1.15)))
            rate = max(0.06, base + hosp_bias + improvement + season + random.uniform(-0.012, 0.012))
            readmits = round(discharges * rate)
            monthly.append({"hospital_id": hid, "month": month, "condition": cond,
                            "discharges": discharges, "readmissions": readmits})

hospitals = []
for hid, name, region, beds in HOSPITALS:
    rows = [m for m in monthly if m["hospital_id"] == hid]
    d = sum(r["discharges"] for r in rows)
    r = sum(r["readmissions"] for r in rows)
    q = REGION_BIAS[region]
    hospitals.append({
        "hospital_id": hid, "hospital_name": name, "region": region, "staffed_beds": beds,
        "discharges_12m": d, "readmissions_12m": r,
        "readmission_rate": round(100 * r / d, 1),
        "hcahps_star": max(1, min(5, round(3.6 - q * 60 + random.uniform(-0.9, 0.9)))),
        "ed_median_minutes": int(150 + beds * 0.12 + q * 2500 + random.uniform(-20, 20)),
        "sep1_compliance_pct": round(min(92, 64 - q * 400 + random.uniform(-6, 8)), 1),
        "clabsi_sir": round(max(0.3, 0.85 + q * 15 + random.uniform(-0.3, 0.3)), 2),
    })

with open(DATA / "hospitals.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(hospitals[0].keys()))
    w.writeheader(); w.writerows(hospitals)
with open(DATA / "monthly_readmissions.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(monthly[0].keys()))
    w.writeheader(); w.writerows(monthly)
with open(DATA / "dashboard_data.json", "w") as f:
    json.dump({"months": MONTHS, "conditions": list(CONDITIONS), "hospitals": hospitals,
               "monthly": monthly}, f, separators=(",", ":"))
print(f"{len(hospitals)} hospitals, {len(monthly)} monthly rows written to {DATA}")
