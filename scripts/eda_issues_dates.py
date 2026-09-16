import pandas as pd
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_csv("data/processed/issues_clean.csv")

# Convert dates
df["created_at"] = pd.to_datetime(df["created_at"])
df["updated_at"] = pd.to_datetime(df["updated_at"])
df["closed_at"] = pd.to_datetime(df["closed_at"])

print("\n==============================")
print("EDA - DATE ANALYSIS")
print("==============================")

# 1. Earliest and latest issue
print("\n1. Earliest Issue Created:")
print(df["created_at"].min())

print("\n2. Latest Issue Created:")
print(df["created_at"].max())

# 2. Date range
date_range = df["created_at"].max() - df["created_at"].min()

print("\n3. Total Date Range:")
print(date_range)

# 3. Issues by date
issues_per_day = df["created_at"].dt.date.value_counts().sort_index()

print("\n4. Issues Per Day:")
print(issues_per_day)

# 4. Issues by hour
print("\n5. Issues By Hour:")
print(df["created_at"].dt.hour.value_counts().sort_index())

# 5. Plot issues per day
plt.figure(figsize=(12, 5))

issues_per_day.plot(kind="line", marker="o")

plt.title("Issues Created Per Day")
plt.xlabel("Date")
plt.ylabel("Number of Issues")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# 6. Calculate issue age for closed issues
closed = df[df["closed_at"].notna()].copy()

closed["resolution_time_hours"] = (
    closed["closed_at"] - closed["created_at"]
).dt.total_seconds() / 3600

print("\n6. Resolution Time Statistics (hours):")
print(closed["resolution_time_hours"].describe())