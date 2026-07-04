# Power BI Customer Churn Analysis Guide

## Data Source
- File: `../excel/churn_analysis.xlsx`
- Primary Sheet: **Raw Data**

## Data Model Setup
1. **Get Data** → Excel → Select `churn_analysis.xlsx` → Check **Raw Data**
2. **Transform Data** (Power Query):
   - Promote headers if needed
   - Change data types:
     - `customer_id` → Text
     - `senior_citizen`, `partner`, `dependents`, `phone_service`, `paperless_billing`, `churn` → True/False (or keep as text for slicers)
     - `tenure`, `monthly_charges`, `total_charges` → Decimal Number
     - All others → Text
   - Create calculated columns:
     - `Churn Label` = if [churn] = 1 then "Yes" else "No"
     - `Tenure Group` = if [tenure] <= 12 then "0-12" else if [tenure] <= 24 then "13-24" else if [tenure] <= 48 then "25-48" else "49+"
     - `Monthly Charges Group` = if [monthly_charges] <= 35 then "Low" else if [monthly_charges] <= 55 then "Medium" else if [monthly_charges] <= 80 then "High" else "Very High"
     - `High Risk` = if [contract] = "Month-to-month" and [tenure] < 12 and [monthly_charges] > 70 then "High Risk" else "Low Risk"

## Key Measures (DAX)

```dax
Total Customers = COUNTROWS('Raw Data')

Churned Customers = CALCULATE([Total Customers], 'Raw Data'[churn] = 1)

Retained Customers = CALCULATE([Total Customers], 'Raw Data'[churn] = 0)

Churn Rate = DIVIDE([Churned Customers], [Total Customers], 0)

Avg Tenure = AVERAGE('Raw Data'[tenure])

Avg Monthly Charges = AVERAGE('Raw Data'[monthly_charges])

Avg Total Charges = AVERAGE('Raw Data'[total_charges])

Avg Tenure Churned = CALCULATE(AVERAGE('Raw Data'[tenure]), 'Raw Data'[churn] = 1)

Avg Tenure Retained = CALCULATE(AVERAGE('Raw Data'[tenure]), 'Raw Data'[churn] = 0)

Avg Monthly Churned = CALCULATE(AVERAGE('Raw Data'[monthly_charges]), 'Raw Data'[churn] = 1)

Avg Monthly Retained = CALCULATE(AVERAGE('Raw Data'[monthly_charges]), 'Raw Data'[churn] = 0)

Monthly Revenue Loss = CALCULATE(SUM('Raw Data'[monthly_charges]), 'Raw Data'[churn] = 1)

Annual Revenue Loss = [Monthly Revenue Loss] * 12

High Risk Customers = CALCULATE([Total Customers], 'Raw Data'[High Risk] = "High Risk")

High Risk Churn Rate = CALCULATE([Churn Rate], 'Raw Data'[High Risk] = "High Risk")
```

## Report Pages

### Page 1: Executive Dashboard
**KPI Cards (Top Row):**
- Total Customers
- Churn Rate %
- Monthly Revenue Loss ($)
- Annual Revenue Loss ($)
- High Risk Customers

**Visuals:**
- **Donut Chart**: Churn Distribution (Churned vs Retained)
- **Stacked Bar Chart**: Churn Rate by Contract Type
- **Stacked Bar Chart**: Churn Rate by Internet Service
- **Stacked Bar Chart**: Churn Rate by Payment Method
- **Slicers** (right side): Contract, Internet Service, Payment Method, Gender, Senior Citizen

### Page 2: Customer Demographics
- **Clustered Column Chart**: Churn Rate by Gender
- **Clustered Column Chart**: Churn Rate by Senior Citizen
- **Clustered Column Chart**: Churn Rate by Partner/Dependents
- **Matrix**: Churn Rate by Contract × Internet Service
- **Slicers**: All demographic fields

### Page 3: Tenure & Charges Analysis
- **Line Chart**: Churn Rate by Tenure Group (x-axis: Tenure Group, y-axis: Churn Rate)
- **Box Plot**: Tenure by Churn (Churned vs Retained)
- **Box Plot**: Monthly Charges by Churn
- **Scatter Plot**: Tenure vs Monthly Charges (color by Churn)
- **Histogram**: Monthly Charges Distribution (Churned vs Retained overlay)

### Page 4: Service Analysis
- **Matrix/Heatmap**: Service combinations impact on churn
  - Rows: Online Security, Online Backup, Device Protection, Tech Support
  - Columns: Streaming TV, Streaming Movies
  - Values: Churn Rate
- **Stacked Bar**: Number of Services vs Churn Rate
- **Key Insight Card**: "Customers with 0-1 add-on services have X% churn vs Y% for 3+ services"

### Page 5: High Risk Customers
- **Table**: Top 20 High Risk Customers
  - Columns: Customer ID, Tenure, Monthly Charges, Contract, Internet Service, Payment Method, Total Charges, Risk Level
  - Conditional Formatting: Monthly Charges (Red gradient)
- **Card**: Count of High Risk Customers
- **Card**: Potential Revenue at Risk (Sum of Monthly Charges for High Risk)
- **Slicer**: Risk Level (High/Low)

### Page 6: Retention Insights
- **Waterfall Chart**: Revenue impact (Retained Revenue vs Lost Revenue)
- **Key Influencers Visual**: What drives churn (Churn as target)
- **Decomposition Tree**: Churn Rate by multiple dimensions
- **Text Box**: Key Recommendations

## Visual Formatting
- **Colors**: 
  - Churned: #FF6B6B (Red)
  - Retained: #4ECDC4 (Teal)
  - High Risk: #FF6B6B
  - Low Risk: #4ECDC4
- **Theme**: Dark or Light (consistent)
- **Fonts**: Segoe UI, 12pt for labels, 14pt for titles

## Interactivity
- **Bookmarks**: Create views for "All", "High Risk Only", "Month-to-Month Only"
- **Drillthrough**: Right-click customer → Drillthrough to Customer Detail page
- **Tooltips**: Custom tooltip page with customer details

## Publish & Share
1. Publish to Power BI Service
2. Set up scheduled refresh (if using gateway)
3. Create Dashboard with pinned tiles
4. Share with stakeholders
5. Set up alerts on Churn Rate KPI (>  > 30%

## Customer Detail Drillthrough Page
- Page name: "Customer Detail"
- Drillthrough filter: Customer ID
- Visuals: Customer profile card, service usage, tenure timeline, charges history, risk factors