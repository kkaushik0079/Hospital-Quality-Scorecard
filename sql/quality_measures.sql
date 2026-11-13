-- Hospital Quality Scorecard: measure calculations
-- Works in SQLite, Postgres and Snowflake (standard SQL).
-- Load data/hospitals.csv into table `hospitals`
-- and data/monthly_readmissions.csv into table `monthly_readmissions`.

-- 1. Data quality checks before reporting
SELECT 'missing hospital' AS check_name, COUNT(*) AS failures
FROM monthly_readmissions m
LEFT JOIN hospitals h ON h.hospital_id = m.hospital_id
WHERE h.hospital_id IS NULL
UNION ALL
SELECT 'readmissions exceed discharges', COUNT(*)
FROM monthly_readmissions WHERE readmissions > discharges
UNION ALL
SELECT 'negative or null counts', COUNT(*)
FROM monthly_readmissions
WHERE discharges IS NULL OR readmissions IS NULL OR discharges <= 0 OR readmissions < 0
UNION ALL
SELECT 'months per hospital/condition not equal to 12', COUNT(*)
FROM (SELECT hospital_id, condition, COUNT(DISTINCT month) AS n
      FROM monthly_readmissions GROUP BY hospital_id, condition) t
WHERE n <> 12;

-- 2. System 30-day readmission rate (all conditions), goal <= 17.0%
SELECT ROUND(100.0 * SUM(readmissions) / SUM(discharges), 1) AS readmission_rate_pct
FROM monthly_readmissions;

-- 3. Monthly readmission rate by region (feeds the trend chart)
SELECT h.region, m.month,
       ROUND(100.0 * SUM(m.readmissions) / SUM(m.discharges), 1) AS readmission_rate_pct
FROM monthly_readmissions m
JOIN hospitals h ON h.hospital_id = m.hospital_id
GROUP BY h.region, m.month
ORDER BY h.region, m.month;

-- 4. Hospital ranking by 12-month readmission rate, with goal status
SELECT h.hospital_name, h.region,
       SUM(m.readmissions) AS readmissions,
       SUM(m.discharges)   AS discharges,
       ROUND(100.0 * SUM(m.readmissions) / SUM(m.discharges), 1) AS readmission_rate_pct,
       CASE
         WHEN 100.0 * SUM(m.readmissions) / SUM(m.discharges) <= 17.0 THEN 'Goal met'
         WHEN 100.0 * SUM(m.readmissions) / SUM(m.discharges) <= 17.0 * 1.05 THEN 'Watch'
         ELSE 'Missed'
       END AS status
FROM monthly_readmissions m
JOIN hospitals h ON h.hospital_id = m.hospital_id
GROUP BY h.hospital_name, h.region
ORDER BY readmission_rate_pct DESC;

-- 5. Readmission rate by condition (AMI, HF, PN, COPD)
SELECT condition,
       ROUND(100.0 * SUM(readmissions) / SUM(discharges), 1) AS readmission_rate_pct
FROM monthly_readmissions
GROUP BY condition
ORDER BY readmission_rate_pct DESC;

-- 6. Discharge-weighted system averages for the other measures
SELECT ROUND(SUM(ed_median_minutes * discharges_12m) * 1.0 / SUM(discharges_12m), 0) AS ed_median_minutes,
       ROUND(SUM(sep1_compliance_pct * discharges_12m) / SUM(discharges_12m), 1)      AS sep1_compliance_pct,
       ROUND(SUM(clabsi_sir * discharges_12m) / SUM(discharges_12m), 2)               AS clabsi_sir,
       ROUND(AVG(hcahps_star * 1.0), 1)                                                AS hcahps_avg_star
FROM hospitals;
