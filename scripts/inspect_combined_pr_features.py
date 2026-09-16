import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_PATH = (
    BASE_DIR
    / "data"
    / "features"
    / "combined_pr_features.csv"
)

df = pd.read_csv(INPUT_PATH)

print("=" * 60)
print("COMBINED PR FEATURE INSPECTION")
print("=" * 60)

print("\nShape:")
print(df.shape)

print("\nDuplicate rows:")
print(df.duplicated().sum())

print("\nUnique PRs:")
print(df["pr_number"].nunique())

# ==========================================
# MISSING VALUES
# ==========================================

print("\n" + "=" * 60)
print("MISSING VALUES")
print("=" * 60)

missing = df.isnull().sum()

print(
    missing[missing > 0]
    if (missing > 0).any()
    else "No missing values"
)


# ==========================================
# NUMERIC FEATURES
# ==========================================

numeric_cols = df.select_dtypes(
    include="number"
).columns.tolist()

numeric_cols.remove("pr_number")

print("\n" + "=" * 60)
print("NUMERIC FEATURE STATISTICS")
print("=" * 60)

stats = df[numeric_cols].describe().T

print(stats.to_string())


# ==========================================
# CONSTANT FEATURES
# ==========================================

print("\n" + "=" * 60)
print("CONSTANT FEATURES")
print("=" * 60)

constant_features = []

for col in numeric_cols:

    if df[col].nunique() <= 1:
        constant_features.append(col)

if constant_features:
    for col in constant_features:
        print(col)
else:
    print("None")


# ==========================================
# HIGHLY SKEWED FEATURES
# ==========================================

print("\n" + "=" * 60)
print("SKEWNESS")
print("=" * 60)

skewness = (
    df[numeric_cols]
    .skew()
    .sort_values(ascending=False)
)

print(skewness.to_string())


# ==========================================
# HIGH CORRELATIONS
# ==========================================

print("\n" + "=" * 60)
print("HIGH CORRELATIONS (>|0.90|)")
print("=" * 60)

corr = df[numeric_cols].corr()

found = False

for i in range(len(corr.columns)):

    for j in range(i + 1, len(corr.columns)):

        value = corr.iloc[i, j]

        if abs(value) > 0.90:

            print(
                f"{corr.columns[i]:25} <-> "
                f"{corr.columns[j]:25} = {value:.3f}"
            )

            found = True

if not found:
    print("No correlations above 0.90")


# ==========================================
# NEGATIVE VALUES
# ==========================================

print("\n" + "=" * 60)
print("NEGATIVE VALUES")
print("=" * 60)

negative_found = False

for col in numeric_cols:

    count = (df[col] < 0).sum()

    if count > 0:
        print(f"{col:25} : {count}")
        negative_found = True

if not negative_found:
    print("No negative values")


# ==========================================
# FEATURE TYPES
# ==========================================

print("\n" + "=" * 60)
print("DATA TYPES")
print("=" * 60)

print(df.dtypes.to_string())


print("\n" + "=" * 60)
print("INSPECTION COMPLETED")
print("=" * 60)