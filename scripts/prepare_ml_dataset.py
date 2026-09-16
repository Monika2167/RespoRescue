import pandas as pd
import numpy as np
from pathlib import Path

# ============================================
# REPORESCUE - PREPARE ML DATASET
# ============================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "features"
    / "pr_24h_prediction_features.csv"
)

OUTPUT_DIR = (
    BASE_DIR
    / "data"
    / "ml"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "bottleneck_ml_dataset.csv"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

print("=" * 60)
print("REPORESCUE - PREPARING ML DATASET")
print("=" * 60)

# ============================================
# 1. LOAD DATA
# ============================================

df = pd.read_csv(INPUT_FILE)

print(f"\nInput rows    : {len(df)}")
print(f"Input columns : {len(df.columns)}")

# ============================================
# 2. FEATURES AVAILABLE AT PREDICTION TIME
# ============================================
#
# These features are available during the
# first 24 hours of a PR.
#
# We deliberately DO NOT include:
#
# resolution_time_days
# merge_time_days
# is_closed
# is_merged
# days_since_update
# pr_age_days
#
# because they contain future information.

feature_columns = [
    "title_length",
    "body_length",
    "title_word_count",
    "body_word_count",
    "is_draft",

    "commits_24h",
    "commit_authors_24h",
    "files_changed_24h",
    "additions_24h",
    "deletions_24h",
    "total_changes_24h",

    "changes_per_commit_24h",
    "files_per_commit_24h",
    "deletion_ratio_24h",

    "has_commit_activity_24h",
    "has_file_activity_24h"
]

target_column = "bottleneck_label"

# ============================================
# 3. CHECK REQUIRED COLUMNS
# ============================================

required_columns = (
    feature_columns
    + [target_column]
)

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:

    print("\nERROR: Missing columns:")

    for column in missing_columns:
        print(f" - {column}")

    raise ValueError(
        "Required columns are missing."
    )

print("\nAll required columns found.")

# ============================================
# 4. SELECT ML DATA
# ============================================

ml_df = df[
    required_columns
].copy()

# ============================================
# 5. HANDLE NUMERIC VALUES
# ============================================

numeric_columns = [
    column
    for column in feature_columns
    if column != "is_draft"
]

for column in numeric_columns:

    ml_df[column] = pd.to_numeric(
        ml_df[column],
        errors="coerce"
    )

# ============================================
# 6. HANDLE BOOLEAN FEATURE
# ============================================

ml_df["is_draft"] = (
    ml_df["is_draft"]
    .astype(int)
)

# ============================================
# 7. HANDLE MISSING VALUES
# ============================================

print("\nMissing values before handling:")

missing_before = (
    ml_df.isna().sum()
)

print(
    missing_before[
        missing_before > 0
    ]
)

# Numeric missing values -> median
for column in numeric_columns:

    if ml_df[column].isna().any():

        median_value = (
            ml_df[column]
            .median()
        )

        ml_df[column] = (
            ml_df[column]
            .fillna(median_value)
        )

# ============================================
# 8. TARGET VALIDATION
# ============================================

ml_df[target_column] = pd.to_numeric(
    ml_df[target_column],
    errors="coerce"
)

# Remove any invalid target rows
ml_df = ml_df[
    ml_df[target_column].isin([0, 1])
].copy()

ml_df[target_column] = (
    ml_df[target_column]
    .astype(int)
)

# ============================================
# 9. REMOVE INFINITE VALUES
# ============================================

ml_df = ml_df.replace(
    [np.inf, -np.inf],
    np.nan
)

# Fill any values created by infinity removal
for column in numeric_columns:

    if ml_df[column].isna().any():

        ml_df[column] = (
            ml_df[column]
            .fillna(
                ml_df[column].median()
            )
        )

# ============================================
# 10. FINAL CHECK
# ============================================

print("\n" + "=" * 60)
print("FINAL ML DATASET CHECK")
print("=" * 60)

print(
    f"Rows        : {len(ml_df)}"
)

print(
    f"Features     : {len(feature_columns)}"
)

print(
    f"Total columns: {len(ml_df.columns)}"
)

print(
    f"Duplicate rows: "
    f"{ml_df.duplicated().sum()}"
)

print(
    f"Missing values: "
    f"{ml_df.isna().sum().sum()}"
)

print(
    f"Infinite values: "
    f"{np.isinf(
        ml_df.select_dtypes(
            include=np.number
        )
    ).sum().sum()}"
)

# ============================================
# 11. FEATURE RANGE CHECK
# ============================================

print("\nFeature ranges:")

for column in feature_columns:

    print(
        f"{column:30s}"
        f" min={ml_df[column].min():.4f}"
        f" max={ml_df[column].max():.4f}"
    )

# ============================================
# 12. TARGET DISTRIBUTION
# ============================================

print("\nTarget distribution:")

print(
    ml_df[target_column]
    .value_counts()
    .sort_index()
)

print("\nTarget percentage:")

print(
    (
        ml_df[target_column]
        .value_counts(
            normalize=True
        )
        .sort_index()
        * 100
    ).round(2)
)

# ============================================
# 13. SAVE
# ============================================

ml_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n" + "=" * 60)
print("ML DATASET PREPARATION COMPLETED")
print("=" * 60)

print("Saved to:")
print(OUTPUT_FILE)

print("\nFeatures used:")

for feature in feature_columns:
    print(f" - {feature}")

print("\nTarget:")
print(f" - {target_column}")

print("=" * 60)