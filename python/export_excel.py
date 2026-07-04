import pandas as pd
import numpy as np

df = pd.read_csv('../data/customer_churn_sample.csv')

df['total_charges'] = pd.to_numeric(df['total_charges'], errors='coerce')
df['total_charges'] = df['total_charges'].fillna(df['monthly_charges'] * df['tenure'])

df['churn'] = df['churn'].map({'Yes': 1, 'No': 0})
df['senior_citizen'] = df['senior_citizen'].map({0: 'No', 1: 'Yes'})
df['high_risk'] = np.where(
    (df['contract'] == 'Month-to-month') & 
    (df['tenure'] < 12) & 
    (df['monthly_charges'] > 70), 'High Risk', 'Low Risk'
)

with pd.ExcelWriter('../excel/churn_analysis.xlsx', engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='Raw Data', index=False)
    
    summary = pd.DataFrame({
        'Metric': ['Total Customers', 'Churn Rate %', 'Avg Tenure (months)', 
                   'Avg Monthly Charges', 'Avg Total Charges',
                   'Churned Customers', 'Retained Customers'],
        'Value': [len(df), f"{df['churn'].mean()*100:.1f}%", f"{df['tenure'].mean():.1f}",
                  f"${df['monthly_charges'].mean():.2f}", f"${df['total_charges'].mean():.2f}",
                  df['churn'].sum(), (df['churn']==0).sum()]
    })
    summary.to_excel(writer, sheet_name='Summary', index=False)
    
    for col in ['contract', 'internet_service', 'payment_method', 'gender', 'senior_citizen']:
        pivot = pd.crosstab(df[col], df['churn'], margins=True, normalize='index') * 100
        if pivot.shape[1] == 3:
            pivot.columns = ['Retained %', 'Churned %', 'Total %']
        elif pivot.shape[1] == 2:
            if 0 in pivot.columns and 1 in pivot.columns:
                pivot.columns = ['Retained %', 'Churned %']
            else:
                pivot.columns = [f'{c} %' for c in pivot.columns]
        pivot = pivot.round(1)
        pivot.to_excel(writer, sheet_name=f'Churn by {col[:25]}')
    
    high_risk = df[df['high_risk'] == 'High Risk'].sort_values('monthly_charges', ascending=False)
    high_risk[['customer_id', 'tenure', 'monthly_charges', 'total_charges', 
               'contract', 'internet_service', 'payment_method', 'high_risk']].to_excel(
        writer, sheet_name='High Risk Customers', index=False
    )
    
    tenure_bins = pd.cut(df['tenure'], bins=[0, 12, 24, 48, 72], labels=['0-12', '13-24', '25-48', '49+'])
    tenure_churn = pd.crosstab(tenure_bins, df['churn'], normalize='index') * 100
    if tenure_churn.shape[1] == 2:
        tenure_churn.columns = ['Retained %', 'Churned %']
    tenure_churn = tenure_churn.round(1)
    tenure_churn.to_excel(writer, sheet_name='Churn by Tenure')

print("Excel file created: excel/churn_analysis.xlsx")
print("Sheets: Raw Data, Summary, Churn by Contract, Churn by Internet Service, Churn by Payment Method, Churn by Gender, Churn by Senior Citizen, High Risk Customers, Churn by Tenure")