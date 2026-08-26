import pandas as pd

df = pd.read_csv("supply_chain_demand_forecasting_dataset.csv")

print(df.head())
print(df.shape)
print(df.columns)
print(df.info())
print(df.isnull().sum())
print(df.duplicated().sum())
# Convert Date column to datetime
df["Date"] = pd.to_datetime(df["Date"])

# Check the data types again
print(df.dtypes)

# Check basic statistics
print(df.describe())
# Product-wise total sales
product_sales = df.groupby("Product_Name")["Units_Sold"].sum().sort_values(ascending=False)

print("\nProduct-wise Total Sales:")
print(product_sales)


# Warehouse-wise total sales
warehouse_sales = df.groupby("Warehouse_Location")["Units_Sold"].sum().sort_values(ascending=False)

print("\nWarehouse-wise Total Sales:")
print(warehouse_sales)


# Monthly sales
monthly_sales = df.groupby(df["Date"].dt.to_period("M"))["Units_Sold"].sum()

print("\nMonthly Sales:")
print(monthly_sales)
import matplotlib.pyplot as plt

# Monthly demand trend
monthly_sales = df.groupby(
    df["Date"].dt.to_period("M")
)["Units_Sold"].sum()

monthly_sales.index = monthly_sales.index.astype(str)

plt.figure(figsize=(12, 5))
plt.plot(monthly_sales.index, monthly_sales.values, marker="o")

plt.title("Monthly Demand Trend")
plt.xlabel("Month")
plt.ylabel("Units Sold")
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()
# Product-wise total demand
product_sales = df.groupby("Product_Name")["Units_Sold"].sum().sort_values(ascending=False)

print("\nProduct-wise Total Sales:")
print(product_sales)

# Product-wise sales graph
plt.figure(figsize=(10, 5))

plt.bar(product_sales.index, product_sales.values)

plt.title("Product-wise Total Demand")
plt.xlabel("Product")
plt.ylabel("Total Units Sold")
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()
# Warehouse-wise total demand
warehouse_sales = df.groupby(
    "Warehouse_Location"
)["Units_Sold"].sum().sort_values(ascending=False)

print("\nWarehouse-wise Total Sales:")
print(warehouse_sales)

# Warehouse-wise sales graph
plt.figure(figsize=(8, 5))

plt.bar(warehouse_sales.index, warehouse_sales.values)

plt.title("Warehouse-wise Total Demand")
plt.xlabel("Warehouse")
plt.ylabel("Total Units Sold")

plt.tight_layout()
plt.show()
import sqlite3

# Create SQLite database
conn = sqlite3.connect("supply_chain.db")

print("Database connected successfully!")

conn.close()
# ==============================
# CREATE DATA WAREHOUSE TABLES
# ==============================

import sqlite3

conn = sqlite3.connect("supply_chain.db")
cursor = conn.cursor()

# 1. Product Dimension
cursor.execute("""
CREATE TABLE IF NOT EXISTS Dim_Product (
    Product_ID TEXT PRIMARY KEY,
    Product_Name TEXT,
    Category TEXT,
    Price INTEGER
)
""")

# 2. Warehouse Dimension
cursor.execute("""
CREATE TABLE IF NOT EXISTS Dim_Warehouse (
    Warehouse_ID TEXT PRIMARY KEY,
    Warehouse_Location TEXT
)
""")

# 3. Date Dimension
cursor.execute("""
CREATE TABLE IF NOT EXISTS Dim_Date (
    Date_ID INTEGER PRIMARY KEY,
    Date TEXT,
    Day INTEGER,
    Month INTEGER,
    Year INTEGER
)
""")

# 4. Sales Fact Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Fact_Sales (
    Date_ID INTEGER,
    Product_ID TEXT,
    Warehouse_ID TEXT,
    Units_Sold INTEGER,
    Stock_Available INTEGER,
    Promotion INTEGER,
    Lead_Time_Days INTEGER
)
""")

conn.commit()

print("All Data Warehouse tables created successfully!")

conn.close()
# ==============================
# LOAD DATA INTO DATA WAREHOUSE
# ==============================

import sqlite3
import pandas as pd

# Read dataset
df = pd.read_csv("supply_chain_demand_forecasting_dataset.csv")

# Convert Date
df["Date"] = pd.to_datetime(df["Date"])

# Connect to database
conn = sqlite3.connect("supply_chain.db")

# ------------------------------
# 1. Load Product Dimension
# ------------------------------

products = df[
    ["Product_ID", "Product_Name", "Category", "Price"]
].drop_duplicates()

products.to_sql(
    "Dim_Product",
    conn,
    if_exists="append",
    index=False
)

# ------------------------------
# 2. Load Warehouse Dimension
# ------------------------------

warehouses = df[
    ["Warehouse_ID", "Warehouse_Location"]
].drop_duplicates()

warehouses.to_sql(
    "Dim_Warehouse",
    conn,
    if_exists="append",
    index=False
)

# ------------------------------
# 3. Load Date Dimension
# ------------------------------

dates = pd.DataFrame({
    "Date": df["Date"].drop_duplicates()
})

dates["Day"] = dates["Date"].dt.day
dates["Month"] = dates["Date"].dt.month
dates["Year"] = dates["Date"].dt.year

dates = dates.sort_values("Date").reset_index(drop=True)

dates["Date_ID"] = range(1, len(dates) + 1)

dates["Date"] = dates["Date"].dt.strftime("%Y-%m-%d")

dates = dates[
    ["Date_ID", "Date", "Day", "Month", "Year"]
]

dates.to_sql(
    "Dim_Date",
    conn,
    if_exists="append",
    index=False
)

# Create Date_ID mapping
date_mapping = dates.set_index("Date")["Date_ID"]

# ------------------------------
# 4. Load Fact Sales
# ------------------------------

fact_sales = df.copy()

fact_sales["Date"] = fact_sales["Date"].dt.strftime("%Y-%m-%d")

fact_sales["Date_ID"] = fact_sales["Date"].map(date_mapping)

fact_sales = fact_sales[
    [
        "Date_ID",
        "Product_ID",
        "Warehouse_ID",
        "Units_Sold",
        "Stock_Available",
        "Promotion",
        "Lead_Time_Days"
    ]
]

fact_sales.to_sql(
    "Fact_Sales",
    conn,
    if_exists="append",
    index=False
)

conn.commit()

print("Data loaded successfully into Data Warehouse!")

conn.close()
# ==============================
# VERIFY DATA WAREHOUSE
# ==============================

import sqlite3

conn = sqlite3.connect("supply_chain.db")

tables = [
    "Dim_Product",
    "Dim_Warehouse",
    "Dim_Date",
    "Fact_Sales"
]

for table in tables:
    result = pd.read_sql(
        f"SELECT COUNT(*) AS Total_Rows FROM {table}",
        conn
    )

    print(f"\n{table}:")
    print(result)

conn.close()
# ==============================
# SQL ANALYSIS - TOP PRODUCTS
# ==============================

conn = sqlite3.connect("supply_chain.db")

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

print("\nTop Products by Demand:")
print(result)

conn.close()