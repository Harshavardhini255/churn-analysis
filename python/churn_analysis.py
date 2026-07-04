import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

df = pd.read_csv('../data/customer_churn_sample.csv')

df['total_charges'] = pd.to_numeric(df['total_charges'], errors='coerce')
df['total_charges'] = df['total_charges'].fillna(df['monthly_charges'] * df['tenure'])

df['churn'] = df['churn'].map({'Yes': 1, 'No': 0})
df['senior_citizen'] = df['senior_citizen'].map({0: 'No', 1: 'Yes'})

cat_cols = ['gender', 'partner', 'dependents', 'phone_service', 'multiple_lines', 
            'internet_service', 'online_security', 'online_backup', 'device_protection',
            'tech_support', 'streaming_tv', 'streaming_movies', 'contract', 
            'paperless_billing', 'payment_method', 'senior_citizen']

for col in cat_cols:
    if col in df.columns:
        df[col] = df[col].astype('category')

df.to_csv('outputs/cleaned_churn_data.csv', index=False)

print("Data shape:", df.shape)
print("\nChurn distribution:")
print(df['churn'].value_counts(normalize=True).round(4))
print("\nChurn rate:", df['churn'].mean().round(4))

fig, axes = plt.subplots(2, 3, figsize=(18, 12))

churn_rate = df['churn'].mean()
axes[0,0].pie([churn_rate, 1-churn_rate], labels=['Churned', 'Retained'], 
              autopct='%1.1f%%', colors=['#ff6b6b', '#4ecdc4'])
axes[0,0].set_title('Overall Churn Rate')

churn_by_contract = df.groupby('contract')['churn'].mean().sort_values()
churn_by_contract.plot(kind='barh', ax=axes[0,1], color='#ff6b6b')
axes[0,1].set_title('Churn Rate by Contract Type')
axes[0,1].set_xlabel('Churn Rate')

churn_by_internet = df.groupby('internet_service')['churn'].mean().sort_values()
churn_by_internet.plot(kind='barh', ax=axes[0,2], color='#ff6b6b')
axes[0,2].set_title('Churn Rate by Internet Service')
axes[0,2].set_xlabel('Churn Rate')

sns.boxplot(data=df, x='churn', y='tenure', ax=axes[1,0], palette=['#4ecdc4', '#ff6b6b'])
axes[1,0].set_title('Tenure Distribution by Churn')
axes[1,0].set_xticklabels(['Retained', 'Churned'])

sns.boxplot(data=df, x='churn', y='monthly_charges', ax=axes[1,1], palette=['#4ecdc4', '#ff6b6b'])
axes[1,1].set_title('Monthly Charges by Churn')
axes[1,1].set_xticklabels(['Retained', 'Churned'])

churn_by_payment = df.groupby('payment_method')['churn'].mean().sort_values()
churn_by_payment.plot(kind='barh', ax=axes[1,2], color='#ff6b6b')
axes[1,2].set_title('Churn Rate by Payment Method')
axes[1,2].set_xlabel('Churn Rate')

plt.tight_layout()
plt.savefig('outputs/churn_analysis_charts.png', dpi=300, bbox_inches='tight')
plt.close()

num_cols = ['tenure', 'monthly_charges', 'total_charges']
df_encoded = pd.get_dummies(df.drop('customer_id', axis=1), drop_first=True)
corr_matrix = df_encoded.corr()['churn'].sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(12, 10))
top_corr = corr_matrix.head(15)
bottom_corr = corr_matrix.tail(15)
combined = pd.concat([top_corr, bottom_corr])
combined.plot(kind='barh', ax=ax, color=['#ff6b6b' if x > 0 else '#4ecdc4' for x in combined])
ax.set_title('Top 15 Positive & Negative Correlations with Churn')
ax.set_xlabel('Correlation Coefficient')
plt.tight_layout()
plt.savefig('outputs/churn_correlations.png', dpi=300, bbox_inches='tight')
plt.close()

segment_churn = df.groupby(['contract', 'internet_service', 'tenure']).agg(
    customer_count=('customer_id', 'count'),
    churn_rate=('churn', 'mean'),
    avg_monthly=('monthly_charges', 'mean'),
    avg_tenure=('tenure', 'mean')
).reset_index()

segment_churn['risk_score'] = (segment_churn['churn_rate'] * 0.5 + 
                                (segment_churn['avg_monthly'] / segment_churn['avg_monthly'].max()) * 0.3 +
                                (1 - segment_churn['avg_tenure'] / segment_churn['avg_tenure'].max()) * 0.2)

high_risk = segment_churn.nlargest(10, 'risk_score')
high_risk.to_csv('outputs/high_risk_segments.csv', index=False)

print("\n=== KEY INSIGHTS ===")
print(f"Overall Churn Rate: {churn_rate:.1%}")
print(f"\nChurn by Contract:")
print(df.groupby('contract')['churn'].mean().round(4))
print(f"\nChurn by Internet Service:")
print(df.groupby('internet_service')['churn'].mean().round(4))
print(f"\nChurn by Payment Method:")
print(df.groupby('payment_method')['churn'].mean().round(4))
print(f"\nAvg Tenure - Churned: {df[df['churn']==1]['tenure'].mean():.1f} months")
print(f"Avg Tenure - Retained: {df[df['churn']==0]['tenure'].mean():.1f} months")
print(f"Avg Monthly Charges - Churned: ${df[df['churn']==1]['monthly_charges'].mean():.2f}")
print(f"Avg Monthly Charges - Retained: ${df[df['churn']==0]['monthly_charges'].mean():.2f}")

print("\n=== HIGH RISK SEGMENTS ===")
print(high_risk[['contract', 'internet_service', 'tenure', 'customer_count', 'churn_rate', 'risk_score']])

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score

X = df_encoded.drop('churn', axis=1)
y = df_encoded['churn']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

rf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
rf.fit(X_train, y_train)
y_pred = rf.predict(X_test)
y_prob = rf.predict_proba(X_test)[:, 1]

print("\n=== MODEL PERFORMANCE ===")
print(classification_report(y_test, y_pred))
print(f"ROC-AUC: {roc_auc_score(y_test, y_prob):.4f}")

feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': rf.feature_importances_
}).sort_values('importance', ascending=False).head(15)

fig, ax = plt.subplots(figsize=(10, 8))
feature_importance.plot(kind='barh', x='feature', y='importance', ax=ax, color='#4ecdc4', legend=False)
ax.set_title('Top 15 Feature Importance - Random Forest')
ax.invert_yaxis()
plt.tight_layout()
plt.savefig('outputs/feature_importance.png', dpi=300, bbox_inches='tight')
plt.close()

feature_importance.to_csv('outputs/feature_importance.csv', index=False)

df['risk_score'] = rf.predict_proba(X)[:, 1]
df[['customer_id', 'churn', 'risk_score', 'tenure', 'monthly_charges', 'contract', 'internet_service']].to_csv('outputs/customer_risk_scores.csv', index=False)

high_risk_customers = df.nlargest(10, 'risk_score')[['customer_id', 'churn', 'risk_score', 'tenure', 'monthly_charges', 'contract']]
print("\n=== TOP 10 HIGH RISK CUSTOMERS ===")
print(high_risk_customers)

print("\n=== ANALYSIS COMPLETE ===")
print("Outputs saved to outputs/ folder:")
print("  - cleaned_churn_data.csv")
print("  - churn_analysis_charts.png")
print("  - churn_correlations.png")
print("  - high_risk_segments.csv")
print("  - feature_importance.png")
print("  - feature_importance.csv")
print("  - customer_risk_scores.csv")