import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_PATH = BASE_DIR / "data" / "features" / "issue_features.csv"

df = pd.read_csv(INPUT_PATH)

print("=" * 60)
print("ISSUE FEATURE INSPECTION")
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
    "issue_age_days",
    "days_since_update",
    "resolution_time_days",
    "comments_count",
    "has_comments",
    "has_labels",
    "is_open",
    "activity_score"
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

print("\nis_open distribution:")
print(df["is_open"].value_counts(dropna=False))

print("\nFeature correlations:")
print(
    df[features]
    .corr(numeric_only=True)
    .round(3)
)

print("\n" + "=" * 60)
print("ISSUE FEATURE INSPECTION COMPLETED")
print("=" * 60)