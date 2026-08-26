# Supply Chain Demand Forecasting and Inventory Optimization

## Project Overview

This project is an end-to-end supply chain analytics solution designed to analyze historical sales data, forecast future demand, and support inventory planning decisions.

The project uses Python, SQL, SQLite, and Machine Learning to analyze product and warehouse demand and identify products requiring reorder.

## Objectives

- Analyze historical sales and demand patterns
- Build a supply chain data warehouse using SQLite
- Perform SQL-based business analysis
- Forecast future product demand
- Identify products requiring inventory reorder
- Support inventory optimization decisions

## Technologies Used

- Python
- Pandas
- NumPy
- Matplotlib
- Scikit-learn
- SQL
- SQLite

## Project Features

### 1. Data Analysis
- Monthly demand trend analysis
- Product-wise demand analysis
- Warehouse-wise demand analysis

### 2. Data Warehouse

The project uses a SQLite database with dimension and fact tables for structured supply chain analysis.

### 3. SQL Analysis

SQL queries are used to analyze:
- Product demand
- Monthly demand
- Warehouse performance

### 4. Demand Forecasting

A Linear Regression model is used to forecast future demand.

**Model:** Linear Regression

**MAE:** 264.69 units

**RMSE:** 335.3 units

### 5. Inventory Optimization

The project identifies products requiring reorder using inventory-related analysis such as stock availability, safety stock, and reorder point.

## Key Results

- **Total Demand:** 541,524 units
- **Top Product:** Notebook
- **Top Warehouse:** Delhi
- **Products Requiring Reorder:** 24

### Future Demand Forecast

| Month | Predicted Demand |
|---|---:|
| January 2026 | 22,308 |
| February 2026 | 24,246 |
| March 2026 | 25,710 |

## Dashboard

The project includes a dashboard showing:

- Monthly Demand Trend
- Product-wise Demand
- Warehouse-wise Demand
- Future Demand Forecast
- Total Demand
- Top Product
- Top Warehouse
- Products Requiring Reorder

## Project Structure

```text
supply-chain-demand-forecasting/
│
├── analysis.py
├── sql_analysis.py
├── forecasting.py
├── inventory_optimization.py
├── dashboard.py
├── supply_chain_demand_forecasting_dataset.csv
├── supply_chain.db
├── inventory_optimization_results.csv
└── README.md
