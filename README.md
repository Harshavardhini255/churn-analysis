# Customer Churn Analysis Project

Complete end-to-end churn analysis using SQL, Excel, Python, and Power BI.

## Project Structure

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
└── powerbi/
    └── powerbi_guide.md               # Power BI implementation guide
```

## Key Findings (from Python Analysis)

| Metric | Value |
|--------|-------|
| Overall Churn Rate | 30% |
| Avg Tenure (Churned) | 12 months |
| Avg Tenure (Retained) | 35.6 months |
| Avg Monthly Charges (Churned) | $80.47 |
| Avg Monthly Charges (Retained) | $50.91 |

### High-Risk Segments
- **Contract**: Month-to-month (60% churn)
- **Internet**: Fiber optic (72% churn)
- **Payment**: Electronic check (58% churn)

### Model Performance
- **Random Forest**: 93% accuracy, 0.98 ROC-AUC
- **Top Features**: Contract type, Monthly charges, Tenure, Payment method, Internet service

## How to Run

### Python Analysis
```powershell
cd churn_analysis_project/python
py -3.11 churn_analysis.py
```

### SQL Analysis
Run queries in `sql/churn_analysis.sql` on your database (PostgreSQL/MySQL/SQL Server).

### Excel Analysis
1. Open `excel/churn_analysis.xlsx`
2. Follow `excel/excel_analysis_guide.md`

### Power BI Dashboard
1. Open Power BI Desktop
2. Get Data → CSV → `data/customer_churn_sample.csv`
3. Follow `powerbi/powerbi_guide.md`

## Dependencies
- Python 3.11+
- pandas, numpy, matplotlib, seaborn, scikit-learn, openpyxl
- Install: `py -3.11 -m pip install pandas numpy matplotlib seaborn scikit-learn openpyxl`