import streamlit as st
import sqlite3
import pandas as pd
import numpy as np


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Supply Chain Dashboard",
    page_icon="📦",
    layout="wide"
)


# ==========================================
# TITLE
# ==========================================

st.title("📦 Supply Chain Demand Forecasting")
st.subheader("Demand Analysis & Inventory Optimization")


# ==========================================
# LOAD DATABASE
# ==========================================

@st.cache_data
def load_data():

    conn = sqlite3.connect("supply_chain.db")

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

    data = pd.read_sql(query, conn)

    conn.close()

    data["Date"] = pd.to_datetime(data["Date"])

    return data


df = load_data()


# ==========================================
# LOAD INVENTORY RESULTS
# ==========================================

inventory = pd.read_csv(
    "inventory_optimization_results.csv"
)


# ==========================================
# MONTHLY DEMAND
# ==========================================

monthly = (
    df.groupby(
        df["Date"].dt.to_period("M")
    )["Units_Sold"]
    .sum()
    .reset_index()
)

monthly["Date"] = monthly["Date"].dt.to_timestamp()


# ==========================================
# PRODUCT DEMAND
# ==========================================

product = (
    df.groupby("Product_Name")["Units_Sold"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)


# ==========================================
# WAREHOUSE DEMAND
# ==========================================

warehouse = (
    df.groupby("Warehouse_Location")["Units_Sold"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)


# ==========================================
# KPI VALUES
# ==========================================

total_demand = int(
    df["Units_Sold"].sum()
)

top_product = product.iloc[0]["Product_Name"]

top_warehouse = warehouse.iloc[0]["Warehouse_Location"]

reorder_count = int(
    (inventory["Stock_Status"] == "REORDER").sum()
)


# ==========================================
# KPI CARDS
# ==========================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Demand",
        f"{total_demand:,}"
    )

with col2:
    st.metric(
        "Top Product",
        top_product
    )

with col3:
    st.metric(
        "Top Warehouse",
        top_warehouse
    )

with col4:
    st.metric(
        "Products to Reorder",
        reorder_count
    )


st.divider()


# ==========================================
# MONTHLY DEMAND
# ==========================================

st.header("📈 Monthly Demand Trend")

st.line_chart(
    monthly.set_index("Date")["Units_Sold"]
)


# ==========================================
# PRODUCT & WAREHOUSE ANALYSIS
# ==========================================

col1, col2 = st.columns(2)

with col1:

    st.subheader("📦 Product-wise Demand")

    st.bar_chart(
        product.set_index("Product_Name")
    )


with col2:

    st.subheader("🏭 Warehouse-wise Demand")

    st.bar_chart(
        warehouse.set_index("Warehouse_Location")
    )


# ==========================================
# DEMAND FORECAST
# ==========================================

st.header("🔮 Future Demand Forecast")

forecast = pd.DataFrame({
    "Month": pd.to_datetime([
        "2026-01-01",
        "2026-02-01",
        "2026-03-01"
    ]),

    "Predicted Demand": [
        22308,
        24246,
        25710
    ]
})

st.line_chart(
    forecast.set_index("Month")
)


st.dataframe(
    forecast,
    use_container_width=True
)


# ==========================================
# INVENTORY RECOMMENDATIONS
# ==========================================

st.header("⚠️ Inventory Reorder Recommendations")

reorder = inventory[
    inventory["Stock_Status"] == "REORDER"
]

st.dataframe(
    reorder[
        [
            "Product_Name",
            "Warehouse_Location",
            "Stock_Available",
            "Reorder_Point",
            "Recommended_Order"
        ]
    ],
    use_container_width=True
)


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "Supply Chain Demand Forecasting & Inventory Optimization | "
    "Python • SQL • SQLite • Machine Learning"
)
