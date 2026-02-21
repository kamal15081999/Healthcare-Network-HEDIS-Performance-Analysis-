# 🏥 Healthcare Network HEDIS Performance Analysis (2025)

## 📌 Project Overview

This project analyzes 2024 HEDIS (Healthcare Effectiveness Data and Information Set) performance across a healthcare network. It evaluates provider compliance, assigns performance tiers, and calculates performance-based incentive payouts at both provider and agency levels.

The analysis was conducted using Python and SQLite following structured objectives.

The full implementation is available in the Python script 

# 🎯 Business Objectives

The project addresses the following objectives:

Clean and validate healthcare quality data

Calculate 2024 HEDIS compliance rates

Determine provider and agency tier performance

Calculate network payouts based on performance

Export structured outputs for stakeholder reporting

# 🛠 Technology Stack

Python 3

Pandas

NumPy

SQLite3

CSV exports for reporting

## 📁 Project Structure

```
Healthcare-Network-HEDIS-Analysis/
│
├── Healthcare Analysis.py                 # Main analysis script
├── healthcare_analyst_quiz_data.sqlite    # Source SQLite database
│
├── 2024_hedis_compliance_rates.csv        # Measure-level compliance output
├── agency_payouts_summary.csv             # Agency payout summary
├── provider_performance_detailed.csv      # Provider-level performance detail
│
├── summary.txt                            # Project notes / explanation
├── README.md
│
└── dashboards/                            # Visualization outputs
    ├── kpi_summary.png
    ├── compliance_by_measure.png
    ├── top_agency_payouts.png
    └── tier_distribution.png
```

# 🔎 Step 1: Data Cleaning & Validation
## Business Rule Applied:

If provider_id is missing in the visits table, assume the provider associated with the patient is the provider.

## Cleaning Process:

Converted visit dates to datetime format

Identified and filled missing provider values

Converted compliance flag to numeric

## Validated:

Record counts

Date ranges

Missing compliance data

Unique measures

## Result: Clean, analysis-ready dataset.

# 📊 Step 2: 2024 HEDIS Compliance Calculation

Filtered data to visits occurring in 2024.

## For each measure:

Total visits

Compliant visits

Compliance rate

## Formula:

Compliance Rate = Compliant Visits / Total Visits

Generated output: 2024_hedis_compliance_rates.csv

# 🏥 Step 3: Provider & Agency Tier Performance

Each provider’s compliance rate per measure was calculated.

Tier Assignment Logic
Tier	Condition
Tier 1	compliance_rate ≥ tier_1_cutoff
Tier 2	compliance_rate ≥ tier_2_cutoff
Tier 3	compliance_rate ≥ tier_3_cutoff
No Tier	Below all cutoffs

## Outputs:

Detailed provider performance file

Agency-level average compliance

Qualifying measure counts

Generated output: provider_performance_detailed.csv

# 💰 Step 4: Network Incentive Payouts

Performance-based payouts were calculated based on tier eligibility.

Payout Logic
Tier	Payment Rule
Tier 1	compliant_visits × tier_1_pay_per_compliant_member
Tier 2	compliant_visits × tier_2_pay_per_compliant_member
Tier 3	compliant_visits × tier_3_pay_per_compliant_member
No Tier	$0

## Outputs:

Total payout per agency

Total compliant visits

Number of providers

Average payout per provider

Generated output: agency_payouts_summary.csv

# 📈 Key Insights Enabled

This analysis allows stakeholders to:

Identify top-performing providers and agencies

Evaluate 2024 compliance performance

Assess financial incentive distribution

Benchmark measure-level performance

Support value-based care decision-making

# 🚀 How to Run the Project
## 1️⃣ Install Dependencies
pip install pandas numpy

## 2️⃣ Run the Script
python "Healthcare Analysis.py"


### The script will:

Load SQLite data

Clean & validate

Calculate compliance

Assign tiers

Compute payouts

Export CSV summaries

# 📌 Real-World Relevance

This project reflects real-world healthcare analytics use cases, including:

HEDIS reporting

Value-Based Care models

Pay-for-performance programs

Medicaid/Medicare quality measurement

Provider incentive modeling

# 🧠 Skills Demonstrated

Healthcare data validation

SQL database integration

Compliance rate calculation

Tier-based performance modeling

Financial incentive computation

Aggregation & group-based analytics

Executive-ready CSV reporting

# 👤 Author

Kamal
Healthcare Data Analyst | HEDIS Performance Analytics | Value-Based Care Reporting
