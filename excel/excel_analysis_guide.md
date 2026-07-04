# Customer Churn Analysis - Excel Guide

## 1. Import Data
- Open Excel → Data → Get Data → From Text/CSV
- Select `../data/customer_churn_sample.csv`
- Click Load

## 2. Data Cleaning (Power Query)
- In Power Query Editor:
  - Right-click `total_charges` → Change Type → Decimal Number
  - Add Column → Custom Column:
    ```
    = if [total_charges] = null then [monthly_charges] * [tenure] else [total_charges]
    ```
  - Name: `total_charges_clean`
  - Remove original `total_charges` column
  - Rename `total_charges_clean` to `total_charges`
  - Close & Load

## 3. Create Pivot Tables

### Churn Overview
- Insert → PivotTable → New Worksheet
- Rows: `churn`
- Values: `customer_id` (Count)
- Add Calculated Field: `Churn Rate` = `churn` / Grand Total

### Churn by Contract
- Rows: `contract`, `churn`
- Values: `customer_id` (Count)
- Show Values As → % of Parent Row Total

### Churn by Internet Service
- Rows: `internet_service`, `churn`
- Values: `customer_id` (Count)
- Show Values As → % of Parent Row Total

### Churn by Payment Method
- Rows: `payment_method`, `churn`
- Values: `customer_id` (Count)
- Show Values As → % of Parent Row Total

### Tenure Analysis
- Rows: Group `tenure` (Right-click → Group → By 12 months)
- Columns: `churn`
- Values: `customer_id` (Count)

### Monthly Charges Analysis
- Rows: Group `monthly_charges` (By 20)
- Columns: `churn`
- Values: `customer_id` (Count)

## 4. Create Charts
- Select PivotTable → Insert → Chart
- **Recommended Charts:**
  - 100% Stacked Bar: Churn by Contract/Internet/Payment
  - Clustered Column: Tenure distribution by Churn
  - Box Plot: Monthly Charges by Churn (Insert → Statistical → Box & Whisker)

## 5. Dashboard Sheet
- Create new sheet "Dashboard"
- Arrange charts:
  - Top: KPI Cards (Total Customers, Churn Rate, Avg Tenure, Avg Monthly Charges)
  - Middle: 100% Stacked Bars (Contract, Internet, Payment)
  - Bottom: Tenure & Monthly Charges distributions
- Add Slicers: `contract`, `internet_service`, `payment_method`, `gender`

## 6. Conditional Formatting
- High Risk Customers: Filter `contract` = "Month-to-month" AND `tenure` < 12 AND `monthly_charges` > 70
- Home → Conditional Formatting → Highlight Cells → Greater Than

## 7. Key Formulas
```
Churn Rate: =COUNTIF(churn_range,"Yes")/COUNTA(churn_range)
Avg Tenure Churned: =AVERAGEIF(churn_range,"Yes",tenure_range)
Avg Tenure Retained: =AVERAGEIF(churn_range,"No",tenure_range)
High Risk Flag: =IF(AND(contract="Month-to-month",tenure<12,monthly_charges>70),"High Risk","Low Risk")
```

## 8. Export for Power BI
- Save as `churn_analysis.xlsx` in `excel/` folder
- Ensure all PivotTables refresh on open: Right-click → PivotTable Options → Data → Refresh data when opening file