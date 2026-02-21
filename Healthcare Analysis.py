#!/usr/bin/env python
# coding: utf-8

# In[20]:


import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


# In[21]:


def connect_to_database():
    return sqlite3.connect('healthcare_analyst_quiz_data.sqlite')


# In[22]:


def load_data():
    conn = connect_to_database()
    patients_df = pd.read_sql_query("SELECT * FROM patients", conn)
    providers_df = pd.read_sql_query("SELECT * FROM providers", conn)
    measures_df = pd.read_sql_query("SELECT * FROM measures", conn)
    visits_df = pd.read_sql_query("SELECT * FROM visits", conn)
    
    conn.close()
    
    return patients_df, providers_df, measures_df, visits_df


# In[23]:


def clean_and_validate_data(patients_df, providers_df, measures_df, visits_df):
    """
    Objective 1: Clean and validate healthcare quality data
    Handle missing provider values as specified
    """
    
    visits_df['visit_date'] = pd.to_datetime(visits_df['visit_date'], format='mixed', dayfirst=False)
    
    print(f"Missing provider values in visits: {visits_df['provider_id'].isnull().sum()}")
    
    visits_merged = visits_df.merge(patients_df[['patient_id', 'patient_provider_id']], 
                                   on='patient_id', how='left')
    
    visits_df['provider_id'] = visits_df['provider_id'].fillna(
        visits_merged['patient_provider_id']
    )
    print(f"Missing provider values after cleaning: {visits_df['provider_id'].isnull().sum()}")
    visits_df['compliant'] = pd.to_numeric(visits_df['compliant'], errors='coerce')
    
    print("\nData Validation Summary:")
    print(f"Total patients: {len(patients_df)}")
    print(f"Total providers: {len(providers_df)}")
    print(f"Total measures: {len(measures_df)}")
    print(f"Total visits: {len(visits_df)}")
    print(f"Date range: {visits_df['visit_date'].min()} to {visits_df['visit_date'].max()}")
    print(f"Unique measures: {visits_df['measure_id'].unique()}")
    print(f"Missing compliance data: {visits_df['compliant'].isnull().sum()}")
    
    return visits_df


# In[24]:


def calculate_2024_hedis_compliance(visits_df):
    """
    Objective 2: Calculate 2024 HEDIS measure compliance rates
    """
    visits_2024 = visits_df[visits_df['visit_date'].dt.year == 2024].copy()
    
    print(f"Total 2024 visits: {len(visits_2024)}")
    
    compliance_by_measure = visits_2024.groupby('measure_id').agg({
        'compliant': ['count', 'sum']
    }).round(4)
    
    compliance_by_measure.columns = ['total_visits', 'compliant_visits']
    compliance_by_measure['compliance_rate'] = (
        compliance_by_measure['compliant_visits'] / compliance_by_measure['total_visits']
    ).round(4)
    
    print("\n2024 HEDIS Compliance Rates by Measure:")
    for measure in compliance_by_measure.index:
        rate = compliance_by_measure.loc[measure, 'compliance_rate']
        total = compliance_by_measure.loc[measure, 'total_visits']
        compliant = compliance_by_measure.loc[measure, 'compliant_visits']
        print(f"{measure}: {rate:.2%} ({compliant}/{total} visits)")
    
    overall_compliance = visits_2024['compliant'].mean()
    print(f"\\nOverall 2024 Compliance Rate: {overall_compliance:.2%}")
    
    return compliance_by_measure, visits_2024


# In[25]:


def determine_provider_performance(visits_2024, providers_df, measures_df):
    """
    Objective 3: Determine provider and agency tier performance
    """
    
    provider_compliance = visits_2024.groupby(['provider_id', 'measure_id']).agg({
        'compliant': ['count', 'sum']
    }).reset_index()
    
    provider_compliance.columns = ['provider_id', 'measure_id', 'total_visits', 'compliant_visits']
    provider_compliance['compliance_rate'] = (
        provider_compliance['compliant_visits'] / provider_compliance['total_visits']
    )
    
    provider_performance = provider_compliance.merge(measures_df, on='measure_id')
    
    def determine_tier(row):
        rate = row['compliance_rate']
        if rate >= row['tier_1_cutoff']:
            return 'Tier 1'
        elif rate >= row['tier_2_cutoff']:
            return 'Tier 2'
        elif rate >= row['tier_3_cutoff']:
            return 'Tier 3'
        else:
            return 'No Tier'
    
    provider_performance['tier'] = provider_performance.apply(determine_tier, axis=1)
    
    provider_performance = provider_performance.merge(
        providers_df[['provider_id', 'provider_name', 'provider_agency_name']], 
        on='provider_id'
    )
    
    tier_summary = provider_performance['tier'].value_counts()
    for tier in ['Tier 1', 'Tier 2', 'Tier 3', 'No Tier']:
        if tier in tier_summary.index:
            print(f"{tier}: {tier_summary[tier]} provider-measure combinations")
    
    agency_performance = provider_performance.groupby('provider_agency_name').agg({
        'compliance_rate': 'mean',
        'tier': lambda x: (x != 'No Tier').sum(),
        'provider_id': 'nunique'
    }).round(4)
    
    agency_performance.columns = ['avg_compliance_rate', 'qualifying_measures', 'num_providers']
    agency_performance = agency_performance.sort_values('avg_compliance_rate', ascending=False)
    
    print("\nTop 10 Agency Performance (by average compliance rate):")
    for agency in agency_performance.head(10).index:
        rate = agency_performance.loc[agency, 'avg_compliance_rate']
        measures = agency_performance.loc[agency, 'qualifying_measures']
        providers = agency_performance.loc[agency, 'num_providers']
        print(f"{agency}: {rate:.2%} avg compliance, {measures} qualifying measures, {providers} providers")
    
    return provider_performance, agency_performance

def calculate_network_payouts(provider_performance):
    """
    Objective 4: Calculate network payouts to agencies based on performance
    """
    
    def calculate_payout(row):
        if row['tier'] == 'Tier 1':
            return row['compliant_visits'] * row['tier_1_pay_per_compliant_member']
        elif row['tier'] == 'Tier 2':
            return row['compliant_visits'] * row['tier_2_pay_per_compliant_member']
        elif row['tier'] == 'Tier 3':
            return row['compliant_visits'] * row['tier_3_pay_per_compliant_member']
        else:
            return 0
    
    provider_performance['payout'] = provider_performance.apply(calculate_payout, axis=1)
    
    agency_payouts = provider_performance.groupby('provider_agency_name').agg({
        'payout': 'sum',
        'compliant_visits': 'sum',
        'total_visits': 'sum',
        'provider_id': 'nunique'
    }).round(2)
    
    agency_payouts.columns = ['total_payout', 'total_compliant_visits', 'total_visits', 'num_providers']
    agency_payouts['avg_payout_per_provider'] = (agency_payouts['total_payout'] / 
                                                 agency_payouts['num_providers']).round(2)
    agency_payouts = agency_payouts.sort_values('total_payout', ascending=False)
    
    print("\nTop 10 Agency Payouts:")
    for agency in agency_payouts.head(10).index:
        payout = agency_payouts.loc[agency, 'total_payout']
        providers = agency_payouts.loc[agency, 'num_providers']
        avg_per_provider = agency_payouts.loc[agency, 'avg_payout_per_provider']
        print(f"{agency}: ${payout:,.2f} total (${avg_per_provider:,.2f}/provider, {providers} providers)")
    
    provider_payouts = provider_performance.groupby(['provider_id', 'provider_name']).agg({
        'payout': 'sum',
        'compliant_visits': 'sum'
    }).sort_values('payout', ascending=False)
    
    print("\nTop 10 Individual Provider Payouts:")
    for (provider_id, provider_name) in provider_payouts.head(10).index:
        payout = provider_payouts.loc[(provider_id, provider_name), 'payout']
        visits = provider_payouts.loc[(provider_id, provider_name), 'compliant_visits']
        print(f"{provider_name} ({provider_id}): ${payout:,.2f} ({visits} compliant visits)")
    
    return agency_payouts, provider_payouts


# In[27]:


def main():
    """Main execution function"""
    print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    patients_df, providers_df, measures_df, visits_df = load_data()
    visits_df_clean = clean_and_validate_data(patients_df, providers_df, measures_df, visits_df)
    compliance_by_measure, visits_2024 = calculate_2024_hedis_compliance(visits_df_clean)
    provider_performance, agency_performance = determine_provider_performance(
        visits_2024, providers_df, measures_df)
    
    agency_payouts, provider_payouts = calculate_network_payouts(provider_performance)
    compliance_by_measure.to_csv('2024_hedis_compliance_rates.csv')
    agency_payouts.to_csv('agency_payouts_summary.csv')
    provider_performance.to_csv('provider_performance_detailed.csv', index=False)

if __name__ == "__main__":
    main()


# In[ ]:




