import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st


# ==========================================
# CONNECT TO DATA WAREHOUSE
# ==========================================

conn = sqlite3.connect("supply_chain.db")


# ==========================================
# 1. MONTHLY DEMAND
# ==========================================

monthly_query = """
SELECT
    d.Year,
    d.Month,
    SUM(f.Units_Sold) AS Total_Demand
FROM Fact_Sales f
JOIN Dim_Date d
    ON f.Date_ID = d.Date_ID
GROUP BY d.Year, d.Month
ORDER BY d.Year, d.Month
"""

monthly = pd.read_sql(monthly_query, conn)

monthly["Date"] = pd.to_datetime(
    monthly["Year"].astype(str)
    + "-"
    + monthly["Month"].astype(str)
    + "-01"
)


# ==========================================
# 2. PRODUCT-WISE DEMAND
# ==========================================

product_query = """
SELECT
    p.Product_Name,
    SUM(f.Units_Sold) AS Total_Demand
FROM Fact_Sales f
JOIN Dim_Product p
    ON f.Product_ID = p.Product_ID
GROUP BY p.Product_Name
ORDER BY Total_Demand DESC
"""

product = pd.read_sql(product_query, conn)


# ==========================================
# 3. WAREHOUSE-WISE DEMAND
# ==========================================

warehouse_query = """
SELECT
    w.Warehouse_Location,
    SUM(f.Units_Sold) AS Total_Demand
FROM Fact_Sales f
JOIN Dim_Warehouse w
    ON f.Warehouse_ID = w.Warehouse_ID
GROUP BY w.Warehouse_Location
ORDER BY Total_Demand DESC
"""

warehouse = pd.read_sql(warehouse_query, conn)

conn.close()


# ==========================================
# 4. INVENTORY DATA
# ==========================================

inventory = pd.read_csv(
    "inventory_optimization_results.csv"
)

reorder_count = (
    inventory["Stock_Status"] == "REORDER"
).sum()


# ==========================================
# 5. FORECAST DATA
# ==========================================

forecast_dates = pd.to_datetime([
    "2026-01-01",
    "2026-02-01",
    "2026-03-01"
])

forecast_values = [
    22308,
    24246,
    25710
]


# ==========================================
# 6. KEY INFORMATION
# ==========================================

total_demand = monthly["Total_Demand"].sum()

top_product = product.iloc[0]["Product_Name"]

top_warehouse = warehouse.iloc[0]["Warehouse_Location"]


# ==========================================
# 7. CREATE DASHBOARD
# ==========================================

fig = plt.figure(figsize=(16, 10))

fig.suptitle(
    "SUPPLY CHAIN DEMAND FORECASTING & INVENTORY OPTIMIZATION",
    fontsize=18,
    fontweight="bold"
)


# ==========================================
# CHART 1 - MONTHLY DEMAND
# ==========================================

ax1 = plt.subplot(2, 2, 1)

ax1.plot(
    monthly["Date"],
    monthly["Total_Demand"],
    marker="o"
)

ax1.set_title(
    "Monthly Demand Trend",
    fontsize=13,
    fontweight="bold"
)

ax1.set_xlabel("Month")
ax1.set_ylabel("Units Sold")

ax1.tick_params(
    axis="x",
    rotation=45
)

ax1.grid(
    True,
    alpha=0.3
)


# ==========================================
# CHART 2 - PRODUCT DEMAND
# ==========================================

ax2 = plt.subplot(2, 2, 2)

ax2.bar(
    product["Product_Name"],
    product["Total_Demand"]
)

ax2.set_title(
    "Product-wise Demand",
    fontsize=13,
    fontweight="bold"
)

ax2.set_xlabel("Product")
ax2.set_ylabel("Units Sold")

ax2.tick_params(
    axis="x",
    rotation=45
)


# ==========================================
# CHART 3 - WAREHOUSE DEMAND
# ==========================================

ax3 = plt.subplot(2, 2, 3)

ax3.bar(
    warehouse["Warehouse_Location"],
    warehouse["Total_Demand"]
)

ax3.set_title(
    "Warehouse-wise Demand",
    fontsize=13,
    fontweight="bold"
)

ax3.set_xlabel("Warehouse")
ax3.set_ylabel("Units Sold")


# ==========================================
# CHART 4 - FUTURE FORECAST
# ==========================================

ax4 = plt.subplot(2, 2, 4)

ax4.plot(
    monthly["Date"],
    monthly["Total_Demand"],
    marker="o",
    label="Historical"
)

ax4.plot(
    forecast_dates,
    forecast_values,
    marker="o",
    linestyle="--",
    label="Forecast"
)

ax4.set_title(
    "Future Demand Forecast",
    fontsize=13,
    fontweight="bold"
)

ax4.set_xlabel("Month")
ax4.set_ylabel("Units Sold")

ax4.legend()

ax4.tick_params(
    axis="x",
    rotation=45
)

ax4.grid(
    True,
    alpha=0.3
)


# ==========================================
# 8. DASHBOARD SUMMARY
# ==========================================

summary = (
    f"Total Demand: {total_demand:,} units     |     "
    f"Top Product: {top_product}     |     "
    f"Top Warehouse: {top_warehouse}     |     "
    f"Products Requiring Reorder: {reorder_count}"
)


fig.text(
    0.5,
    0.025,
    summary,
    ha="center",
    fontsize=12,
    fontweight="bold"
)


# ==========================================
# 9. FINAL LAYOUT
# ==========================================

plt.tight_layout(
    rect=[0, 0.07, 1, 0.94]
)

st.pyplot(fig)
# ==========================================
# 10. TERMINAL SUMMARY
# ==========================================

print("\n==========================================")
print("DASHBOARD COMPLETED")
print("==========================================")

print(
    "\nTotal Demand:",
    f"{total_demand:,}",
    "units"
)

print(
    "Top Product:",
    top_product
)

print(
    "Top Warehouse:",
    top_warehouse
)

print(
    "Products Requiring Reorder:",
    reorder_count
)

print(
    "\nDashboard displayed successfully."
)
