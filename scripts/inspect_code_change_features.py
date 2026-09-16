import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_PATH = (
    BASE_DIR
    / "data"
    / "features"
    / "pr_code_change_features.csv"
)

df = pd.read_csv(INPUT_PATH)

print("=" * 60)
print("CODE-CHANGE FEATURE INSPECTION")
print("=" * 60)

print("\nShape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nMissing values:")
print(df.isnull().sum())

print("\nDuplicate rows:")
print(df.duplicated().sum())

print("\nUnique PRs:")
print(df["pr_number"].nunique())

print("\n" + "=" * 60)
print("FEATURE STATISTICS")
print("=" * 60)

numeric_cols = df.select_dtypes(include="number").columns

print(
    df[numeric_cols]
    .describe()
    .T
)

print("\n" + "=" * 60)
print("ZERO VALUES")
print("=" * 60)

for col in numeric_cols:
    if col != "pr_number":
        zero_count = (df[col] == 0).sum()
        print(f"{col:25} : {zero_count}")

print("\n" + "=" * 60)
print("NEGATIVE VALUES")
print("=" * 60)

for col in numeric_cols:
    if col != "pr_number":
        negative_count = (df[col] < 0).sum()
        print(f"{col:25} : {negative_count}")

print("\n" + "=" * 60)
print("TOP 10 HIGHEST CODE-CHANGE PRs")
print("=" * 60)

print(
    df.nlargest(10, "total_changes")[
        [
            "pr_number",
            "commits_count",
            "files_changed",
            "additions",
            "deletions",
            "total_changes",
            "developers_involved"
        ]
    ].to_string(index=False)
)

print("\n" + "=" * 60)
print("INSPECTION COMPLETED")
print("=" * 60)