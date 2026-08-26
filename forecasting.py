import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error


# ==========================================
# 1. CONNECT TO DATA WAREHOUSE
# ==========================================

conn = sqlite3.connect("supply_chain.db")


# ==========================================
# 2. GET MONTHLY DEMAND FROM DATA WAREHOUSE
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

df = pd.read_sql(query, conn)

conn.close()


# ==========================================
# 3. CREATE DATE COLUMN
# ==========================================

df["Date"] = pd.to_datetime(
    df["Year"].astype(str) + "-" +
    df["Month"].astype(str) + "-01"
)

df = df.sort_values("Date").reset_index(drop=True)


# ==========================================
# 4. CREATE FEATURES
# ==========================================

df["Time_Index"] = range(len(df))

df["Month_Sin"] = np.sin(
    2 * np.pi * df["Month"] / 12
)

df["Month_Cos"] = np.cos(
    2 * np.pi * df["Month"] / 12
)


# ==========================================
# 5. TRAIN / TEST SPLIT
# ==========================================

# First 18 months = Training
# Last 6 months = Testing

train = df.iloc[:18]
test = df.iloc[18:]

features = [
    "Time_Index",
    "Month_Sin",
    "Month_Cos"
]

X_train = train[features]
y_train = train["Total_Demand"]

X_test = test[features]
y_test = test["Total_Demand"]


# ==========================================
# 6. TRAIN MACHINE LEARNING MODEL
# ==========================================

model = LinearRegression()

model.fit(X_train, y_train)


# ==========================================
# 7. PREDICT TEST DATA
# ==========================================

test["Predicted_Demand"] = model.predict(X_test)


# ==========================================
# 8. MODEL ACCURACY
# ==========================================

mae = mean_absolute_error(
    y_test,
    test["Predicted_Demand"]
)

rmse = np.sqrt(
    mean_squared_error(
        y_test,
        test["Predicted_Demand"]
    )
)

print("\n==========================================")
print("DEMAND FORECASTING MODEL")
print("==========================================")

print("\nModel: Linear Regression")

print("\nMean Absolute Error (MAE):")
print(round(mae, 2))

print("\nRoot Mean Squared Error (RMSE):")
print(round(rmse, 2))


# ==========================================
# 9. TEST DATA VS PREDICTION
# ==========================================

print("\n==========================================")
print("ACTUAL VS PREDICTED DEMAND")
print("==========================================")

comparison = test[
    ["Date", "Total_Demand", "Predicted_Demand"]
].copy()

comparison["Predicted_Demand"] = comparison[
    "Predicted_Demand"
].round(0)

print(comparison.to_string(index=False))


# ==========================================
# 10. FUTURE DEMAND FORECAST
# ==========================================

# Train model using ALL historical data

X_all = df[features]
y_all = df["Total_Demand"]

final_model = LinearRegression()

final_model.fit(X_all, y_all)


# Create next 3 months

future_dates = pd.date_range(
    start=df["Date"].max() + pd.DateOffset(months=1),
    periods=3,
    freq="MS"
)

future = pd.DataFrame({
    "Date": future_dates
})

future["Year"] = future["Date"].dt.year
future["Month"] = future["Date"].dt.month

future["Time_Index"] = range(
    len(df),
    len(df) + len(future)
)

future["Month_Sin"] = np.sin(
    2 * np.pi * future["Month"] / 12
)

future["Month_Cos"] = np.cos(
    2 * np.pi * future["Month"] / 12
)


# Predict future demand

future["Predicted_Demand"] = final_model.predict(
    future[features]
)

future["Predicted_Demand"] = (
    future["Predicted_Demand"]
    .round(0)
    .astype(int)
)


# ==========================================
# 11. DISPLAY FUTURE FORECAST
# ==========================================

print("\n==========================================")
print("FUTURE DEMAND FORECAST")
print("==========================================")

print(
    future[
        ["Date", "Predicted_Demand"]
    ].to_string(index=False)
)


# ==========================================
# 12. FORECAST GRAPH
# ==========================================

plt.figure(figsize=(12, 6))

plt.plot(
    df["Date"],
    df["Total_Demand"],
    marker="o",
    label="Historical Demand"
)

plt.plot(
    future["Date"],
    future["Predicted_Demand"],
    marker="o",
    linestyle="--",
    label="Forecasted Demand"
)

plt.title("Demand Forecasting")
plt.xlabel("Date")
plt.ylabel("Units Sold")

plt.legend()
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()


print("\n==========================================")
print("FORECASTING COMPLETED")
print("==========================================")