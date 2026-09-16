import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_PATH = BASE_DIR / "data" / "features" / "pr_features.csv"

df = pd.read_csv(INPUT_PATH)

print("=" * 60)
print("PR FEATURE INSPECTION")
print("=" * 60)

print("\nShape:")
print(df.shape)

print("\nMissing values:")
missing = df.isna().sum()
print(missing[missing > 0])

print("\nDuplicate rows:")
print(df.duplicated().sum())

features = [
    "title_length",
    "body_length",
    "title_word_count",
    "body_word_count",
    "pr_age_days",
    "days_since_update",
    "resolution_time_days",
    "merge_time_days",
    "is_open",
    "is_closed",
    "is_merged",
    "is_draft",
    "author_pr_count"
]

print("\nFeature statistics:")
print(df[features].describe().T)

print("\nNegative values:")
for col in features:
    count = (df[col] < 0).sum()
    if count > 0:
        print(f"{col}: {count}")

print("\nState distribution:")
print(df["state"].value_counts(dropna=False))

print("\nMerge status:")
print(df["is_merged"].value_counts(dropna=False))

print("\nDraft status:")
print(df["is_draft"].value_counts(dropna=False))

print("\nOpen/Closed consistency:")

print(
    "Open but is_open = 0:",
    ((df["state"].str.lower() == "open") & (df["is_open"] == 0)).sum()
)

print(
    "Closed but is_closed = 0:",
    ((df["state"].str.lower() == "closed") & (df["is_closed"] == 0)).sum()
)

print("\n" + "=" * 60)
print("PR FEATURE INSPECTION COMPLETED")
print("=" * 60)