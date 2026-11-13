# Hospital Quality Scorecard

An interactive quality dashboard for a fictional 10-hospital system, tracking the measures hospital leadership reviews every month: 30-day readmissions, patient experience, emergency department throughput, sepsis care and infection control.

**Live demo:** [https://kkaushik0079.github.io/Hospital-Quality-Scorecard/]

> **All data is synthetic.** Hospital names are fictional, and no values come from CMS or any real hospital. Measure definitions are modeled on public CMS quality programs.

## What it shows

| Measure | Modeled on | System goal |
|---|---|---|
| 30-day readmission rate (AMI, HF, PN, COPD) | CMS Hospital Readmissions Reduction Program | ≤ 17.0% |
| Overall hospital rating | HCAHPS star rating | ≥ 4.0 stars |
| Median time from ED arrival to departure | OP-18b | ≤ 180 min |
| Severe sepsis bundle compliance | SEP-1 | ≥ 65% |
| Central line infections | NHSN CLABSI standardized infection ratio (SIR) | ≤ 1.00 |

Features:
- **KPI strip** with goal status (goal met, watch if within 5% of goal, or missed)
- **Monthly readmission trend by region**, with a goal line and a hover tooltip for each month
- **Hospital ranking** by 12-month readmission rate
- **Scorecard table** with a status for every hospital and measure
- **Filters** by region and readmission condition. Every chart and the table update together.
- Works on desktop and phone, in light and dark mode

## How it's built

```
healthcare-kpi-dashboard/
├── index.html                  # the dashboard (plain HTML, CSS, JavaScript; no framework)
├── data/
│   ├── hospitals.csv           # one row per hospital, 12-month measures
│   ├── monthly_readmissions.csv  # 480 rows: hospital × month × condition
│   └── dashboard_data.json     # same data shaped for the page
├── scripts/generate_data.py    # creates the synthetic dataset
└── sql/quality_measures.sql    # data-quality checks + every measure in SQL
```

- **Data generation (Python):** `generate_data.py` builds realistic patterns, including regional differences, winter seasonality and gradual improvement over the year, using a fixed random seed so the results are reproducible.
- **Data quality (SQL):** before any reporting, `quality_measures.sql` checks for orphan records, readmissions exceeding discharges, invalid counts, and missing months.
- **Measures (SQL):** readmission rates are calculated as total readmissions ÷ total discharges, not as an average of monthly rates, so larger hospitals carry proper weight. Other system measures are discharge-weighted.
- **Visualization:** charts are drawn as SVG from scratch, with a colorblind-safe palette that has been checked for contrast in light and dark mode.

## Run it locally

```bash
python scripts/generate_data.py   # optional: regenerate the data
# then open index.html in a browser
```

To reproduce the measures in a database, load the two CSVs as tables `hospitals` and `monthly_readmissions` and run `sql/quality_measures.sql`.

## Skills demonstrated

Healthcare quality measures · SQL data validation and KPI logic · Python · data visualization · dashboard design · stakeholder-ready reporting

---
Built by **Kritika Kaushik** · [LinkedIn](https://www.linkedin.com/in/kkaushik0079-mba/)
