import sqlite3
import pandas as pd
import numpy as np


# ==========================================
# 1. CONNECT TO DATA WAREHOUSE
# ==========================================

conn = sqlite3.connect("supply_chain.db")


# ==========================================
# 2. GET SALES AND STOCK DATA
# ==========================================

query = """
SELECT
    f.Date_ID,
    d.Date,
    f.Product_ID,
    p.Product_Name,
    f.Warehouse_ID,
    w.Warehouse_Location,
    f.Units_Sold,
    f.Stock_Available,
    f.Lead_Time_Days
FROM Fact_Sales f

JOIN Dim_Date d
    ON f.Date_ID = d.Date_ID

JOIN Dim_Product p
    ON f.Product_ID = p.Product_ID

JOIN Dim_Warehouse w
    ON f.Warehouse_ID = w.Warehouse_ID
"""

df = pd.read_sql(query, conn)

conn.close()


# ==========================================
# 3. CONVERT DATE
# ==========================================

df["Date"] = pd.to_datetime(df["Date"])


# ==========================================
# 4. CALCULATE AVERAGE DAILY DEMAND
# ==========================================

product_stats = df.groupby(
    ["Product_ID", "Product_Name", "Warehouse_ID", "Warehouse_Location"]
).agg(
    Average_Daily_Demand=("Units_Sold", "mean"),
    Demand_Std=("Units_Sold", "std"),
    Average_Lead_Time=("Lead_Time_Days", "mean")
).reset_index()


# ==========================================
# 5. GET CURRENT STOCK
# ==========================================

latest_date = df["Date"].max()

latest_stock = df[
    df["Date"] == latest_date
][
    [
        "Product_ID",
        "Product_Name",
        "Warehouse_ID",
        "Warehouse_Location",
        "Stock_Available"
    ]
]

latest_stock = latest_stock.drop_duplicates(
    ["Product_ID", "Warehouse_ID"]
)


# ==========================================
# 6. MERGE STATISTICS WITH CURRENT STOCK
# ==========================================

inventory = product_stats.merge(
    latest_stock,
    on=[
        "Product_ID",
        "Product_Name",
        "Warehouse_ID",
        "Warehouse_Location"
    ],
    how="left"
)


# ==========================================
# 7. CALCULATE SAFETY STOCK
# ==========================================

# 95% service level
Z = 1.65

inventory["Safety_Stock"] = (
    Z
    * inventory["Demand_Std"].fillna(0)
    * np.sqrt(inventory["Average_Lead_Time"])
)


# ==========================================
# 8. CALCULATE REORDER POINT
# ==========================================

inventory["Reorder_Point"] = (
    inventory["Average_Daily_Demand"]
    * inventory["Average_Lead_Time"]
    + inventory["Safety_Stock"]
)


# ==========================================
# 9. CALCULATE RECOMMENDED ORDER
# ==========================================

inventory["Recommended_Order"] = (
    inventory["Reorder_Point"]
    - inventory["Stock_Available"]
)

inventory["Recommended_Order"] = (
    inventory["Recommended_Order"]
    .clip(lower=0)
    .round()
    .astype(int)
)


# ==========================================
# 10. STOCK STATUS
# ==========================================

inventory["Stock_Status"] = np.where(
    inventory["Stock_Available"]
    <= inventory["Reorder_Point"],
    "REORDER",
    "SUFFICIENT"
)


# ==========================================
# 11. ROUND VALUES
# ==========================================

inventory["Average_Daily_Demand"] = (
    inventory["Average_Daily_Demand"].round(2)
)

inventory["Average_Lead_Time"] = (
    inventory["Average_Lead_Time"].round(2)
)

inventory["Safety_Stock"] = (
    inventory["Safety_Stock"].round()
)

inventory["Reorder_Point"] = (
    inventory["Reorder_Point"].round()
)


# ==========================================
# 12. DISPLAY INVENTORY RECOMMENDATIONS
# ==========================================

print("\n==========================================")
print("INVENTORY OPTIMIZATION")
print("==========================================")

print("\nLatest Data Date:", latest_date.date())

print("\nInventory Recommendations:")

result = inventory[
    [
        "Product_Name",
        "Warehouse_Location",
        "Stock_Available",
        "Average_Daily_Demand",
        "Safety_Stock",
        "Reorder_Point",
        "Recommended_Order",
        "Stock_Status"
    ]
]

print(result.to_string(index=False))


# ==========================================
# 13. SHOW PRODUCTS THAT NEED REORDER
# ==========================================

reorder = inventory[
    inventory["Stock_Status"] == "REORDER"
]

print("\n==========================================")
print("PRODUCTS REQUIRING REORDER")
print("==========================================")

if len(reorder) == 0:

    print("No products currently require reorder.")

else:

    reorder_result = reorder[
        [
            "Product_Name",
            "Warehouse_Location",
            "Stock_Available",
            "Reorder_Point",
            "Recommended_Order"
        ]
    ]

    print(
        reorder_result.to_string(index=False)
    )


# ==========================================
# 14. SAVE RESULTS
# ==========================================

inventory.to_csv(
    "inventory_optimization_results.csv",
    index=False
)

print("\n==========================================")
print("RESULT SAVED")
print("==========================================")

print(
    "inventory_optimization_results.csv created successfully."
)

print("\n==========================================")
print("INVENTORY OPTIMIZATION COMPLETED")
print("==========================================")