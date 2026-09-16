import pandas as pd
from pathlib import Path

# ============================================
# REPORESCUE - INSPECT 24-HOUR FEATURES
# ============================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "features"
    / "pr_24h_prediction_features.csv"
)

df = pd.read_csv(INPUT_FILE)

print("=" * 60)
print("24-HOUR PREDICTION FEATURE INSPECTION")
print("=" * 60)

print(f"\nShape: {df.shape}")

# ============================================
# 1. BASIC CHECK
# ============================================

print("\n--- BASIC CHECK ---")

print(f"Duplicate rows: {df.duplicated().sum()}")
print(
    f"Duplicate PRs : "
    f"{df['pr_number'].duplicated().sum()}"
)

print("\nMissing values:")

missing = df.isna().sum()
missing = missing[missing > 0]

if len(missing) == 0:
    print("None")
else:
    print(missing)

# ============================================
# 2. TARGET DISTRIBUTION
# ============================================

print("\n--- TARGET DISTRIBUTION ---")

print(
    df["bottleneck_label"]
    .value_counts()
)

print("\nTarget percentages:")

print(
    (
        df["bottleneck_label"]
        .value_counts(normalize=True)
        * 100
    ).round(2)
)

# ============================================
# 3. FEATURE STATISTICS
# ============================================

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

print("\n--- FEATURE STATISTICS ---")

print(
    df[feature_columns]
    .describe()
    .T
)

# ============================================
# 4. ZERO-ACTIVITY ANALYSIS
# ============================================

activity_columns = [
    "commits_24h",
    "files_changed_24h",
    "additions_24h",
    "deletions_24h",
    "total_changes_24h"
]

print("\n--- ZERO-ACTIVITY ANALYSIS ---")

for column in activity_columns:

    zero_count = (
        df[column] == 0
    ).sum()

    percentage = (
        zero_count
        / len(df)
        * 100
    )

    print(
        f"{column:25s}: "
        f"{zero_count:5d} "
        f"({percentage:.2f}%)"
    )

# ============================================
# 5. ACTIVITY BY TARGET
# ============================================

print("\n--- ACTIVITY BY TARGET ---")

target_activity = df.groupby(
    "bottleneck_label"
)[
    [
        "commits_24h",
        "commit_authors_24h",
        "files_changed_24h",
        "additions_24h",
        "deletions_24h",
        "total_changes_24h"
    ]
].mean()

print(
    target_activity.round(2)
)

# ============================================
# 6. TEXT FEATURES BY TARGET
# ============================================

print("\n--- TEXT FEATURES BY TARGET ---")

text_target = df.groupby(
    "bottleneck_label"
)[
    [
        "title_length",
        "body_length",
        "title_word_count",
        "body_word_count"
    ]
].mean()

print(
    text_target.round(2)
)

# ============================================
# 7. CORRELATION WITH TARGET
# ============================================

print("\n--- CORRELATION WITH TARGET ---")

numeric_features = df[
    feature_columns
].copy()

numeric_features[
    "bottleneck_label"
] = df["bottleneck_label"]

correlations = (
    numeric_features
    .corr()["bottleneck_label"]
    .drop("bottleneck_label")
    .sort_values(
        ascending=False
    )
)

print(
    correlations.round(4)
)

# ============================================
# 8. CONSTANT FEATURES
# ============================================

print("\n--- CONSTANT FEATURES ---")

constant_features = []

for column in feature_columns:

    if df[column].nunique() <= 1:
        constant_features.append(column)

if constant_features:
    print(constant_features)
else:
    print("No constant features found.")

# ============================================
# 9. FINAL STATUS
# ============================================

print("\n" + "=" * 60)
print("24-HOUR FEATURE INSPECTION COMPLETED")
print("=" * 60)