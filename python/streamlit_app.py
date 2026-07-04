import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import os
warnings.filterwarnings('ignore')

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix, roc_curve
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Customer Churn Analysis", layout="wide", page_icon="📊")

@st.cache_data
def load_data():
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, '..', 'data', 'customer_churn_sample.csv')
    df = pd.read_csv(data_path)
    df['total_charges'] = pd.to_numeric(df['total_charges'], errors='coerce')
    df['total_charges'] = df['total_charges'].fillna(df['monthly_charges'] * df['tenure'])
    df['churn_binary'] = df['churn'].map({'Yes': 1, 'No': 0})
    return df

@st.cache_data
def train_model(df):
    # Drop non-numeric columns that can't be encoded
    df_model = df.drop(['customer_id', 'churn'], axis=1)
    
    # Convert all object columns to numeric via one-hot encoding
    df_encoded = pd.get_dummies(df_model, drop_first=True)
    
    # Ensure all columns are numeric
    for col in df_encoded.columns:
        df_encoded[col] = pd.to_numeric(df_encoded[col], errors='coerce')
    
    # Fill any NaN values
    df_encoded = df_encoded.fillna(0)
    
    X = df_encoded.drop('churn_binary', axis=1)
    y = df_encoded['churn_binary']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
    
    rf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
    rf.fit(X_train, y_train)
    
    y_pred = rf.predict(X_test)
    y_prob = rf.predict_proba(X_test)[:, 1]
    
    return rf, X, y, X_test, y_test, y_pred, y_prob

df = load_data()
rf, X, y, X_test, y_test, y_pred, y_prob = train_model(df)

# Sidebar
st.sidebar.title("📊 Customer Churn Analysis")
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigate", [
    "🏠 Executive Dashboard",
    "📈 EDA & Visualizations", 
    "🤖 ML Model & Predictions",
    "🎯 High-Risk Customers",
    "📋 SQL Queries Reference",
    "📁 Project Files"
])

# ===== PAGE 1: EXECUTIVE DASHBOARD =====
if page == "🏠 Executive Dashboard":
    st.title("🏠 Executive Dashboard - Customer Churn Analysis")
    
    # KPIs
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Customers", len(df))
    with col2:
        st.metric("Churn Rate", f"{df['churn_binary'].mean()*100:.1f}%")
    with col3:
        st.metric("Avg Tenure (months)", f"{df['tenure'].mean():.1f}")
    with col4:
        st.metric("Avg Monthly Charges", f"${df['monthly_charges'].mean():.2f}")
    with col5:
        monthly_loss = df[df['churn_binary']==1]['monthly_charges'].sum()
        st.metric("Monthly Revenue Loss", f"${monthly_loss:.2f}")
    
    st.markdown("---")
    
    # Charts row 1
    col1, col2 = st.columns(2)
    
    with col1:
        churn_counts = df['churn'].value_counts()
        fig = px.pie(values=churn_counts.values, names=churn_counts.index, 
                     title="Overall Churn Distribution",
                     color_discrete_map={'Yes': '#FF6B6B', 'No': '#4ECDC4'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        contract_churn = pd.crosstab(df['contract'], df['churn'], normalize='index') * 100
        fig = px.bar(contract_churn, x=contract_churn.index, y='Yes',
                     title="Churn Rate by Contract Type",
                     labels={'x': 'Contract', 'y': 'Churn Rate (%)'},
                     color_discrete_sequence=['#FF6B6B'])
        st.plotly_chart(fig, use_container_width=True)
    
    # Charts row 2
    col1, col2 = st.columns(2)
    
    with col1:
        internet_churn = pd.crosstab(df['internet_service'], df['churn'], normalize='index') * 100
        fig = px.bar(internet_churn, x=internet_churn.index, y='Yes',
                     title="Churn Rate by Internet Service",
                     labels={'x': 'Internet Service', 'y': 'Churn Rate (%)'},
                     color_discrete_sequence=['#FF6B6B'])
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        payment_churn = pd.crosstab(df['payment_method'], df['churn'], normalize='index') * 100
        fig = px.bar(payment_churn, x=payment_churn.index, y='Yes',
                     title="Churn Rate by Payment Method",
                     labels={'x': 'Payment Method', 'y': 'Churn Rate (%)'},
                     color_discrete_sequence=['#FF6B6B'])
        st.plotly_chart(fig, use_container_width=True)
    
    # Key insights
    st.markdown("### 🔑 Key Insights")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"**Month-to-month contracts**: {df[df['contract']=='Month-to-month']['churn_binary'].mean()*100:.0f}% churn rate")
    with col2:
        st.info(f"**Fiber optic users**: {df[df['internet_service']=='Fiber optic']['churn_binary'].mean()*100:.0f}% churn rate")
    with col3:
        st.info(f"**Electronic check payers**: {df[df['payment_method']=='Electronic check']['churn_binary'].mean()*100:.0f}% churn rate")

# ===== PAGE 2: EDA =====
elif page == "📈 EDA & Visualizations":
    st.title("📈 Exploratory Data Analysis")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Distributions", "Correlations", "Tenure Analysis", "Service Analysis"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            fig = px.box(df, x='churn', y='tenure', color='churn',
                         title="Tenure Distribution by Churn",
                         color_discrete_map={'Yes': '#FF6B6B', 'No': '#4ECDC4'})
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.box(df, x='churn', y='monthly_charges', color='churn',
                         title="Monthly Charges by Churn",
                         color_discrete_map={'Yes': '#FF6B6B', 'No': '#4ECDC4'})
            st.plotly_chart(fig, use_container_width=True)
        
        fig = px.histogram(df, x='monthly_charges', color='churn', barmode='overlay',
                           title="Monthly Charges Distribution (Churned vs Retained)",
                           color_discrete_map={'Yes': '#FF6B6B', 'No': '#4ECDC4'},
                           opacity=0.7)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        cat_cols = df.select_dtypes(include='object').columns.tolist()
        for col in ['churn', 'customer_id']:
            if col in cat_cols:
                cat_cols.remove(col)
        df_encoded = pd.get_dummies(df.drop('customer_id', axis=1), columns=cat_cols, drop_first=True)
        # Ensure all columns are numeric
        for col in df_encoded.columns:
            df_encoded[col] = pd.to_numeric(df_encoded[col], errors='coerce')
        df_encoded = df_encoded.fillna(0)
        corr_matrix = df_encoded.corr()['churn_binary'].sort_values(ascending=False)
        
        top_15 = corr_matrix.head(15)
        bottom_15 = corr_matrix.tail(15)
        combined = pd.concat([top_15, bottom_15])
        
        fig = go.Figure(go.Bar(
            x=combined.values,
            y=combined.index,
            orientation='h',
            marker_color=['#FF6B6B' if x > 0 else '#4ECDC4' for x in combined.values]
        ))
        fig.update_layout(title="Top 15 Positive & Negative Correlations with Churn",
                          xaxis_title="Correlation Coefficient", height=600)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        df['tenure_group'] = pd.cut(df['tenure'], bins=[0, 12, 24, 48, 72], 
                                    labels=['0-12', '13-24', '25-48', '49+'])
        tenure_churn = pd.crosstab(df['tenure_group'], df['churn'], normalize='index') * 100
        
        fig = px.line(x=tenure_churn.index.astype(str), y=tenure_churn['Yes'],
                      markers=True, title="Churn Rate by Tenure Group",
                      labels={'x': 'Tenure Group (months)', 'y': 'Churn Rate (%)'})
        fig.update_traces(line_color='#FF6B6B', marker_color='#FF6B6B')
        st.plotly_chart(fig, use_container_width=True)
        
        fig = px.scatter(df, x='tenure', y='monthly_charges', color='churn',
                         title="Tenure vs Monthly Charges (colored by Churn)",
                         color_discrete_map={'Yes': '#FF6B6B', 'No': '#4ECDC4'},
                         opacity=0.7)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        service_cols = ['online_security', 'online_backup', 'device_protection', 
                       'tech_support', 'streaming_tv', 'streaming_movies']
        
        for col in service_cols:
            if col in df.columns:
                service_churn = pd.crosstab(df[col], df['churn'], normalize='index') * 100
                if 'Yes' in service_churn.columns:
                    fig = px.bar(service_churn, x=service_churn.index, y='Yes',
                                 title=f"Churn Rate by {col.replace('_', ' ').title()}",
                                 labels={'x': col.replace('_', ' ').title(), 'y': 'Churn Rate (%)'},
                                 color_discrete_sequence=['#FF6B6B'])
                    st.plotly_chart(fig, use_container_width=True)

# ===== PAGE 3: ML MODEL =====
elif page == "🤖 ML Model & Predictions":
    st.title("🤖 Machine Learning Model")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Model Performance")
        st.metric("Accuracy", f"{(y_test == y_pred).mean()*100:.1f}%")
        st.metric("ROC-AUC", f"{roc_auc_score(y_test, y_prob):.4f}")
        
        st.text("Classification Report:")
        report = classification_report(y_test, y_pred, output_dict=True)
        st.dataframe(pd.DataFrame(report).transpose().round(3))
    
    with col2:
        # Confusion Matrix
        cm = confusion_matrix(y_test, y_pred)
        fig = px.imshow(cm, text_auto=True, aspect="auto",
                        labels=dict(x="Predicted", y="Actual", color="Count"),
                        x=['Retained', 'Churned'], y=['Retained', 'Churned'],
                        color_continuous_scale='RdYlGn_r')
        fig.update_layout(title="Confusion Matrix")
        st.plotly_chart(fig, use_container_width=True)
    
    # ROC Curve
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=fpr, y=tpr, mode='lines', name=f'Random Forest (AUC = {roc_auc_score(y_test, y_prob):.3f})', line_color='#FF6B6B'))
    fig.add_trace(go.Scatter(x=[0,1], y=[0,1], mode='lines', name='Random', line_dash='dash', line_color='gray'))
    fig.update_layout(title="ROC Curve", xaxis_title="False Positive Rate", yaxis_title="True Positive Rate")
    st.plotly_chart(fig, use_container_width=True)
    
    # Feature Importance
    st.subheader("Feature Importance")
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': rf.feature_importances_
    }).sort_values('importance', ascending=False).head(15)
    
    fig = px.bar(feature_importance, x='importance', y='feature', orientation='h',
                 title="Top 15 Feature Importances - Random Forest",
                 color_discrete_sequence=['#4ECDC4'])
    fig.update_layout(yaxis={'categoryorder': 'total ascending'}, height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # Interactive Prediction
    st.subheader("🎯 Try Prediction")
    st.markdown("Enter customer details to predict churn risk:")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        tenure = st.slider("Tenure (months)", 0, 72, 12)
        monthly = st.slider("Monthly Charges ($)", 18, 120, 70)
    with col2:
        contract = st.selectbox("Contract", ['Month-to-month', 'One year', 'Two year'])
        internet = st.selectbox("Internet Service", ['DSL', 'Fiber optic', 'No'])
    with col3:
        payment = st.selectbox("Payment Method", ['Electronic check', 'Mailed check', 'Bank transfer (automatic)', 'Credit card (automatic)'])
        gender = st.selectbox("Gender", ['Male', 'Female'])
    
    if st.button("Predict Churn Risk"):
        # Simple rule-based for demo
        risk = 0
        if contract == 'Month-to-month': risk += 0.4
        if internet == 'Fiber optic': risk += 0.3
        if payment == 'Electronic check': risk += 0.2
        if tenure < 12: risk += 0.1
        if monthly > 80: risk += 0.1
        
        risk = min(risk, 1.0)
        st.metric("Predicted Churn Probability", f"{risk*100:.0f}%")
        if risk > 0.6:
            st.error("🔴 HIGH RISK - Immediate retention action needed!")
        elif risk > 0.3:
            st.warning("🟡 MEDIUM RISK - Monitor closely")
        else:
            st.success("🟢 LOW RISK - Customer likely to stay")

# ===== PAGE 4: HIGH RISK =====
elif page == "🎯 High-Risk Customers":
    st.title("🎯 High-Risk Customer Segments")
    
    # Risk scoring
    df['risk_score'] = 0
    df.loc[df['contract'] == 'Month-to-month', 'risk_score'] += 3
    df.loc[df['contract'] == 'One year', 'risk_score'] += 2
    df.loc[df['contract'] == 'Two year', 'risk_score'] += 1
    
    df.loc[df['payment_method'] == 'Electronic check', 'risk_score'] += 3
    df.loc[df['payment_method'] == 'Mailed check', 'risk_score'] += 2
    df.loc[df['payment_method'].isin(['Bank transfer (automatic)', 'Credit card (automatic)']), 'risk_score'] += 1
    
    df.loc[df['tenure'] <= 12, 'risk_score'] += 3
    df.loc[(df['tenure'] > 12) & (df['tenure'] <= 24), 'risk_score'] += 2
    df.loc[df['tenure'] > 24, 'risk_score'] += 1
    
    df.loc[df['monthly_charges'] > 80, 'risk_score'] += 3
    df.loc[(df['monthly_charges'] > 50) & (df['monthly_charges'] <= 80), 'risk_score'] += 2
    df.loc[df['monthly_charges'] <= 50, 'risk_score'] += 1
    
    high_risk = df[(df['risk_score'] >= 10) & (df['churn_binary'] == 0)].sort_values('risk_score', ascending=False)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Customers", len(df))
    with col2:
        st.metric("Current Churned", len(df[df['churn_binary']==1]))
    with col3:
        st.metric("High-Risk (Retained)", len(high_risk))
    
    st.subheader("🔴 Top 20 High-Risk Retained Customers")
    display_cols = ['customer_id', 'tenure', 'monthly_charges', 'total_charges', 
                    'contract', 'internet_service', 'payment_method', 'risk_score']
    st.dataframe(high_risk[display_cols].head(20), use_container_width=True)
    
    # Risk distribution
    fig = px.histogram(df, x='risk_score', color='churn', barmode='overlay',
                       title="Risk Score Distribution",
                       color_discrete_map={'Yes': '#FF6B6B', 'No': '#4ECDC4'},
                       opacity=0.7)
    st.plotly_chart(fig, use_container_width=True)
    
    # Segment analysis
    st.subheader("High-Risk Segments")
    segment = df.groupby(['contract', 'internet_service', 'payment_method']).agg(
        count=('customer_id', 'count'),
        churn_rate=('churn_binary', 'mean'),
        avg_monthly=('monthly_charges', 'mean')
    ).reset_index()
    segment['churn_rate'] = (segment['churn_rate'] * 100).round(1)
    segment = segment.sort_values('churn_rate', ascending=False).head(10)
    
    st.dataframe(segment, use_container_width=True)

# ===== PAGE 5: SQL =====
elif page == "📋 SQL Queries Reference":
    st.title("📋 SQL Analysis Queries")
    
    queries = {
        "Overall Churn Rate": """SELECT churn, COUNT(*) as count, ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as rate_pct
FROM customers GROUP BY churn;""",
        "Churn by Contract": """SELECT contract, churn, COUNT(*) as count,
ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY contract), 2) as rate_pct
FROM customers GROUP BY contract, churn ORDER BY contract, churn;""",
        "High-Value at Risk": """SELECT customer_id, monthly_charges, total_charges, tenure, contract
FROM customers WHERE monthly_charges > 80 AND contract = 'Month-to-month' AND churn = 'No'
ORDER BY monthly_charges DESC;""",
        "Tenure Groups": """SELECT CASE WHEN tenure <= 12 THEN '0-12'
WHEN tenure <= 24 THEN '13-24' WHEN tenure <= 48 THEN '25-48' ELSE '49+' END as tenure_group,
churn, COUNT(*) as count FROM customers GROUP BY tenure_group, churn;""",
        "Revenue Impact": """SELECT SUM(CASE WHEN churn='Yes' THEN total_charges ELSE 0 END) as lost_revenue,
SUM(CASE WHEN churn='No' THEN total_charges ELSE 0 END) as retained_revenue,
ROUND(SUM(CASE WHEN churn='Yes' THEN total_charges ELSE 0 END) * 100.0 / SUM(total_charges), 2) as loss_pct
FROM customers;"""
    }
    
    for title, query in queries.items():
        with st.expander(f"📄 {title}"):
            st.code(query, language='sql')

# ===== PAGE 6: PROJECT FILES =====
elif page == "📁 Project Files":
    st.title("📁 Project Structure & Files")
    
    st.markdown("""
    ### Repository: https://github.com/Harshavardhini255/churn-analysis
    
    ```
    churn_analysis_project/
    ├── data/
    │   └── customer_churn_sample.csv      # 50 sample customer records
    ├── sql/
    │   └── churn_analysis.sql             # 15 analytical queries
    ├── python/
    │   ├── churn_analysis.py              # Main analysis script
    │   ├── export_excel.py                # Excel export helper
    │   └── outputs/                       # Generated outputs
    │       ├── churn_analysis_charts.png
    │       ├── churn_correlations.png
    │       ├── feature_importance.png
    │       ├── cleaned_churn_data.csv
    │       ├── customer_risk_scores.csv
    │       ├── feature_importance.csv
    │       └── high_risk_segments.csv
    ├── excel/
    │   ├── churn_analysis.xlsx            # Excel workbook template
    │   └── excel_analysis_guide.md        # Step-by-step Excel guide
    ├── powerbi/
    │   └── powerbi_guide.md               # Power BI implementation guide
    ├── README.md                          # Project overview
    └── streamlit_app.py                   # This Streamlit app
    ```
    """)
    
    st.subheader("🚀 How to Run Locally")
    st.code("""
# 1. Clone repo
git clone https://github.com/Harshavardhini255/churn-analysis.git
cd churn-analysis

# 2. Install dependencies
pip install pandas numpy matplotlib seaborn scikit-learn streamlit plotly

# 3. Run Streamlit app
cd churn_analysis_project/python
streamlit run streamlit_app.py

# 4. Run Python analysis
py -3.11 churn_analysis.py
    """, language='bash')
    
    st.subheader("📊 Key Results Summary")
    results_df = pd.DataFrame({
        'Metric': ['Overall Churn Rate', 'Model Accuracy', 'ROC-AUC', 'Avg Tenure (Churned)', 
                   'Avg Tenure (Retained)', 'Avg Monthly (Churned)', 'Avg Monthly (Retained)',
                   'Monthly Revenue Loss'],
        'Value': ['30%', '93%', '0.98', '12 months', '35.6 months', '$80.47', '$50.91', '$482.80']
    })
    st.dataframe(results_df, use_container_width=True)
    
    st.subheader("🔗 Links")
    st.markdown("""
    - **GitHub Repo**: https://github.com/Harshavardhini255/churn-analysis
    - **Streamlit Cloud**: Deploy this app free at share.streamlit.io
    - **Power BI**: Follow `powerbi/powerbi_guide.md` to build dashboard
    - **Excel**: Open `excel/churn_analysis.xlsx` and follow guide
    """)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**Customer Churn Analysis Project**")
st.sidebar.markdown("Built with Streamlit | GitHub: Harshavardhini255/churn-analysis")