import pandas as pd
from pathlib import Path

# ==========================================
# PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_PATH = (
    BASE_DIR
    / "data"
    / "preprocessed"
    / "pull_requests_preprocessed.csv"
)

OUTPUT_DIR = BASE_DIR / "data" / "features"
OUTPUT_PATH = OUTPUT_DIR / "pr_features.csv"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ==========================================
# LOAD DATA
# ==========================================

print("=" * 60)
print("CREATING PULL REQUEST FEATURES")
print("=" * 60)

df = pd.read_csv(INPUT_PATH)

print("\nLoaded pull requests:", len(df))


# ==========================================
# DATE CONVERSION
# ==========================================

date_columns = [
    "created_at",
    "updated_at",
    "closed_at",
    "merged_at"
]

for col in date_columns:
    df[col] = pd.to_datetime(
        df[col],
        errors="coerce",
        utc=True
    )


# ==========================================
# REFERENCE DATE
# ==========================================

reference_date = df["updated_at"].max()

print("\nReference date:", reference_date)


# ==========================================
# TEXT FEATURES
# ==========================================

df["title_length"] = (
    df["title"]
    .fillna("")
    .astype(str)
    .str.len()
)

df["body_length"] = (
    df["body"]
    .fillna("")
    .astype(str)
    .str.len()
)

df["title_word_count"] = (
    df["title"]
    .fillna("")
    .astype(str)
    .str.split()
    .str.len()
)

df["body_word_count"] = (
    df["body"]
    .fillna("")
    .astype(str)
    .str.split()
    .str.len()
)


# ==========================================
# PR AGE
# ==========================================

df["pr_age_days"] = (
    reference_date - df["created_at"]
).dt.total_seconds() / 86400


# ==========================================
# DAYS SINCE LAST UPDATE
# ==========================================

df["days_since_update"] = (
    reference_date - df["updated_at"]
).dt.total_seconds() / 86400


# ==========================================
# TIME TO CLOSE
# ==========================================
# Only closed PRs will have this value.

df["resolution_time_days"] = (
    df["closed_at"] - df["created_at"]
).dt.total_seconds() / 86400


# ==========================================
# TIME TO MERGE
# ==========================================
# Only merged PRs will have this value.

df["merge_time_days"] = (
    df["merged_at"] - df["created_at"]
).dt.total_seconds() / 86400


# ==========================================
# STATUS FEATURES
# ==========================================

df["is_open"] = (
    df["state"]
    .astype(str)
    .str.lower()
    .eq("open")
    .astype(int)
)

df["is_closed"] = (
    df["state"]
    .astype(str)
    .str.lower()
    .eq("closed")
    .astype(int)
)

df["is_merged"] = (
    df["merged_at"].notna()
).astype(int)

df["is_draft"] = (
    df["draft"]
    .astype(bool)
    .astype(int)
)


# ==========================================
# AUTHOR FEATURE
# ==========================================
# Number of PRs created by each author
# within this collected dataset.

author_pr_counts = df["author"].value_counts()

df["author_pr_count"] = (
    df["author"].map(author_pr_counts).fillna(0)
)


# ==========================================
# CLEAN NUMERICAL FEATURES
# ==========================================

numeric_features = [
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

for col in numeric_features:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )


# ==========================================
# SAVE
# ==========================================

df.to_csv(
    OUTPUT_PATH,
    index=False
)


# ==========================================
# SUMMARY
# ==========================================

print("\n" + "=" * 60)
print("PR FEATURE ENGINEERING COMPLETED")
print("=" * 60)

print("\nRows:", len(df))
print("Columns:", len(df.columns))

print("\nNew features:")

for feature in numeric_features:
    print("  ✓", feature)

print("\nSaved to:")
print(OUTPUT_PATH)