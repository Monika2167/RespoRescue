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
    / "issues_preprocessed.csv"
)

OUTPUT_DIR = BASE_DIR / "data" / "features"
OUTPUT_PATH = OUTPUT_DIR / "issue_features.csv"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ==========================================
# LOAD DATA
# ==========================================

print("=" * 60)
print("CREATING ISSUE FEATURES")
print("=" * 60)

df = pd.read_csv(INPUT_PATH)

print("\nLoaded issues:", len(df))


# ==========================================
# DATE CONVERSION
# ==========================================

df["created_at"] = pd.to_datetime(
    df["created_at"],
    errors="coerce",
    utc=True
)

df["updated_at"] = pd.to_datetime(
    df["updated_at"],
    errors="coerce",
    utc=True
)

df["closed_at"] = pd.to_datetime(
    df["closed_at"],
    errors="coerce",
    utc=True
)


# ==========================================
# REFERENCE DATE
# ==========================================
# We use the latest observed update date in
# the dataset as the reference point.
#
# This prevents using the actual future date
# while constructing historical features.

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
# ISSUE AGE
# ==========================================

df["issue_age_days"] = (
    reference_date - df["created_at"]
).dt.total_seconds() / 86400


# ==========================================
# DAYS SINCE LAST UPDATE
# ==========================================

df["days_since_update"] = (
    reference_date - df["updated_at"]
).dt.total_seconds() / 86400


# ==========================================
# ISSUE LIFETIME
# ==========================================
# Only available for closed issues.
# Open issues remain NaN.

df["resolution_time_days"] = (
    df["closed_at"] - df["created_at"]
).dt.total_seconds() / 86400


# ==========================================
# COMMENT FEATURES
# ==========================================

df["comments_count"] = pd.to_numeric(
    df["comments_count"],
    errors="coerce"
).fillna(0)

df["has_comments"] = (
    df["comments_count"] > 0
).astype(int)


# ==========================================
# LABEL FEATURES
# ==========================================

df["has_labels"] = (
    df["labels"]
    .fillna("NO_LABEL")
    .astype(str)
    .ne("NO_LABEL")
    .astype(int)
)


# ==========================================
# STATE FEATURE
# ==========================================

df["is_open"] = (
    df["state"]
    .astype(str)
    .str.lower()
    .eq("open")
    .astype(int)
)


# ==========================================
# ACTIVITY FEATURE
# ==========================================
# Simple indicator of an issue that has
# both comments and recent activity.

df["activity_score"] = (
    df["comments_count"] * 0.5
    + df["has_comments"]
    + (1 / (1 + df["days_since_update"].clip(lower=0)))
)


# ==========================================
# CLEAN NUMERICAL FEATURES
# ==========================================

numeric_features = [
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
print("ISSUE FEATURE ENGINEERING COMPLETED")
print("=" * 60)

print("\nRows:", len(df))
print("Columns:", len(df.columns))

print("\nNew features:")

for feature in numeric_features:
    print("  ✓", feature)

print("\nSaved to:")
print(OUTPUT_PATH)