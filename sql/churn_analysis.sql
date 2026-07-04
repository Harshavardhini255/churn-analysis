-- Customer Churn Analysis SQL Scripts
-- Database: CustomerChurnDB

-- 1. Create Tables
CREATE TABLE customers (
    customer_id VARCHAR(20) PRIMARY KEY,
    gender VARCHAR(10),
    senior_citizen INT,
    partner VARCHAR(3),
    dependents VARCHAR(3),
    tenure INT,
    phone_service VARCHAR(3),
    multiple_lines VARCHAR(20),
    internet_service VARCHAR(20),
    online_security VARCHAR(20),
    online_backup VARCHAR(20),
    device_protection VARCHAR(20),
    tech_support VARCHAR(20),
    streaming_tv VARCHAR(20),
    streaming_movies VARCHAR(20),
    contract VARCHAR(20),
    paperless_billing VARCHAR(3),
    payment_method VARCHAR(30),
    monthly_charges DECIMAL(10,2),
    total_charges DECIMAL(10,2),
    churn VARCHAR(3)
);

-- 2. Load Data (PostgreSQL example)
-- COPY customers FROM 'data/customer_churn_sample.csv' DELIMITER ',' CSV HEADER;

-- 3. Basic Churn Rate Analysis
SELECT 
    churn,
    COUNT(*) as customer_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as churn_rate_pct
FROM customers
GROUP BY churn;

-- 4. Churn by Contract Type
SELECT 
    contract,
    churn,
    COUNT(*) as customer_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY contract), 2) as churn_rate_pct
FROM customers
GROUP BY contract, churn
ORDER BY contract, churn;

-- 5. Churn by Payment Method
SELECT 
    payment_method,
    churn,
    COUNT(*) as customer_count,
    ROUND(AVG(monthly_charges), 2) as avg_monthly_charges
FROM customers
GROUP BY payment_method, churn
ORDER BY payment_method, churn;

-- 6. Churn by Internet Service Type
SELECT 
    internet_service,
    churn,
    COUNT(*) as customer_count,
    ROUND(AVG(monthly_charges), 2) as avg_monthly_charges,
    ROUND(AVG(tenure), 1) as avg_tenure
FROM customers
GROUP BY internet_service, churn
ORDER BY internet_service, churn;

-- 7. High-Value Customers at Risk (Monthly Charges > 80, Month-to-month contract)
SELECT 
    customer_id,
    monthly_charges,
    total_charges,
    tenure,
    contract,
    internet_service
FROM customers
WHERE monthly_charges > 80 
    AND contract = 'Month-to-month'
    AND churn = 'No'
ORDER BY monthly_charges DESC;

-- 8. Tenure Analysis - Churn by Tenure Groups
SELECT 
    CASE 
        WHEN tenure <= 12 THEN '0-12 months'
        WHEN tenure <= 24 THEN '13-24 months'
        WHEN tenure <= 48 THEN '25-48 months'
        ELSE '49+ months'
    END as tenure_group,
    churn,
    COUNT(*) as customer_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY CASE 
        WHEN tenure <= 12 THEN '0-12 months'
        WHEN tenure <= 24 THEN '13-24 months'
        WHEN tenure <= 48 THEN '25-48 months'
        ELSE '49+ months'
    END), 2) as churn_rate_pct
FROM customers
GROUP BY tenure_group, churn
ORDER BY tenure_group, churn;

-- 9. Senior Citizen Churn Analysis
SELECT 
    senior_citizen,
    churn,
    COUNT(*) as customer_count,
    ROUND(AVG(monthly_charges), 2) as avg_monthly_charges
FROM customers
GROUP BY senior_citizen, churn
ORDER BY senior_citizen, churn;

-- 10. Service Bundles Impact on Churn
SELECT 
    online_security,
    online_backup,
    device_protection,
    tech_support,
    churn,
    COUNT(*) as customer_count
FROM customers
WHERE internet_service != 'No'
GROUP BY online_security, online_backup, device_protection, tech_support, churn
ORDER BY online_security, online_backup, device_protection, tech_support, churn;

-- 11. Customer Lifetime Value (CLV) Estimation
SELECT 
    customer_id,
    tenure,
    monthly_charges,
    total_charges,
    CASE 
        WHEN churn = 'Yes' THEN total_charges
        ELSE total_charges + (monthly_charges * (24 - tenure))
    END as estimated_clv
FROM customers
ORDER BY estimated_clv DESC;

-- 12. Monthly Charges Distribution by Churn
SELECT 
    churn,
    MIN(monthly_charges) as min_charges,
    MAX(monthly_charges) as max_charges,
    ROUND(AVG(monthly_charges), 2) as avg_charges,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY monthly_charges), 2) as median_charges
FROM customers
GROUP BY churn;

-- 13. Churn Risk Scoring
SELECT 
    customer_id,
    CASE 
        WHEN contract = 'Month-to-month' THEN 3
        WHEN contract = 'One year' THEN 2
        ELSE 1
    END as contract_risk,
    CASE 
        WHEN payment_method = 'Electronic check' THEN 3
        WHEN payment_method = 'Mailed check' THEN 2
        ELSE 1
    END as payment_risk,
    CASE 
        WHEN tenure <= 12 THEN 3
        WHEN tenure <= 24 THEN 2
        ELSE 1
    END as tenure_risk,
    CASE 
        WHEN monthly_charges > 80 THEN 3
        WHEN monthly_charges > 50 THEN 2
        ELSE 1
    END as charges_risk,
    (CASE 
        WHEN contract = 'Month-to-month' THEN 3
        WHEN contract = 'One year' THEN 2
        ELSE 1
    END +
    CASE 
        WHEN payment_method = 'Electronic check' THEN 3
        WHEN payment_method = 'Mailed check' THEN 2
        ELSE 1
    END +
    CASE 
        WHEN tenure <= 12 THEN 3
        WHEN tenure <= 24 THEN 2
        ELSE 1
    END +
    CASE 
        WHEN monthly_charges > 80 THEN 3
        WHEN monthly_charges > 50 THEN 2
        ELSE 1
    END) as total_risk_score
FROM customers
WHERE churn = 'No'
ORDER BY total_risk_score DESC;

-- 14. Retention Campaign Targets
SELECT 
    customer_id,
    tenure,
    monthly_charges,
    contract,
    internet_service,
    payment_method,
    total_charges
FROM customers
WHERE churn = 'No'
    AND contract = 'Month-to-month'
    AND tenure <= 12
    AND monthly_charges > 50
ORDER BY monthly_charges DESC;

-- 15. Revenue Impact of Churn
SELECT 
    SUM(CASE WHEN churn = 'Yes' THEN total_charges ELSE 0 END) as lost_revenue,
    SUM(CASE WHEN churn = 'No' THEN total_charges ELSE 0 END) as retained_revenue,
    ROUND(
        SUM(CASE WHEN churn = 'Yes' THEN total_charges ELSE 0 END) * 100.0 / 
        SUM(total_charges), 2
    ) as revenue_loss_pct
FROM customers;