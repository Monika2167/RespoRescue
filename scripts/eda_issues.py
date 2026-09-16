import pandas as pd

# Load dataset
df = pd.read_csv("data/processed/issues_clean.csv")

print("\n==============================")
print("EDA - ISSUES DATASET")
print("==============================")

# 1. Dataset shape
print("\n1. Dataset Shape:")
print(df.shape)

# 2. Column names
print("\n2. Columns:")
print(df.columns.tolist())

# 3. Data types
print("\n3. Data Types:")
print(df.dtypes)

# 4. First 5 rows
print("\n4. First 5 Rows:")
print(df.head())

# 5. Statistical summary
print("\n5. Statistical Summary:")
print(df.describe(include="all"))

# 6. Missing values
print("\n6. Missing Values:")
print(df.isnull().sum())

# 7. Duplicate rows
print("\n7. Duplicate Rows:")
print(df.duplicated().sum())