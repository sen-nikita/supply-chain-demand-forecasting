import sqlite3
import pandas as pd

# Connect to existing Data Warehouse
conn = sqlite3.connect("supply_chain.db")


# ==========================================
# 1. TOP PRODUCTS BY DEMAND
# ==========================================

query = """
SELECT 
    p.Product_Name,
    SUM(f.Units_Sold) AS Total_Demand
FROM Fact_Sales f
JOIN Dim_Product p
    ON f.Product_ID = p.Product_ID
GROUP BY p.Product_Name
ORDER BY Total_Demand DESC;
"""

result = pd.read_sql(query, conn)

print("\n==============================")
print("TOP PRODUCTS BY DEMAND")
print("==============================")
print(result)


# ==========================================
# 2. WAREHOUSE-WISE DEMAND
# ==========================================

query = """
SELECT
    w.Warehouse_Location,
    SUM(f.Units_Sold) AS Total_Demand
FROM Fact_Sales f
JOIN Dim_Warehouse w
    ON f.Warehouse_ID = w.Warehouse_ID
GROUP BY w.Warehouse_Location
ORDER BY Total_Demand DESC;
"""

result = pd.read_sql(query, conn)

print("\n==============================")
print("WAREHOUSE-WISE DEMAND")
print("==============================")
print(result)


# ==========================================
# 3. MONTHLY DEMAND
# ==========================================

query = """
SELECT
    d.Year,
    d.Month,
    SUM(f.Units_Sold) AS Total_Demand
FROM Fact_Sales f
JOIN Dim_Date d
    ON f.Date_ID = d.Date_ID
GROUP BY d.Year, d.Month
ORDER BY d.Year, d.Month;
"""

result = pd.read_sql(query, conn)

print("\n==============================")
print("MONTHLY DEMAND")
print("==============================")
print(result)


# ==========================================
# CLOSE DATABASE
# ==========================================

conn.close()

print("\n==============================")
print("SQL ANALYSIS COMPLETED")
print("==============================")