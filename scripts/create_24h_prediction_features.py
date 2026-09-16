import pandas as pd
import numpy as np
from pathlib import Path

# ============================================
# REPORESCUE
# CREATE 24-HOUR PREDICTION FEATURES
# ============================================

BASE_DIR = Path(__file__).resolve().parent.parent

PR_FILE = (
    BASE_DIR
    / "data"
    / "preprocessed"
    / "pull_requests_preprocessed.csv"
)

COMMITS_FILE = (
    BASE_DIR
    / "data"
    / "preprocessed"
    / "commits_preprocessed.csv"
)

FILES_FILE = (
    BASE_DIR
    / "data"
    / "preprocessed"
    / "files_preprocessed.csv"
)

LABEL_FILE = (
    BASE_DIR
    / "data"
    / "features"
    / "pr_bottleneck_labels.csv"
)

OUTPUT_DIR = (
    BASE_DIR
    / "data"
    / "features"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "pr_24h_prediction_features.csv"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

print("=" * 60)
print("REPORESCUE - 24-HOUR PREDICTION FEATURES")
print("=" * 60)

# ============================================
# 1. LOAD DATA
# ============================================

print("\nLoading datasets...")

prs = pd.read_csv(PR_FILE)
commits = pd.read_csv(COMMITS_FILE)
files = pd.read_csv(FILES_FILE)
labels = pd.read_csv(LABEL_FILE)

print(f"Pull Requests : {len(prs)}")
print(f"Commits       : {len(commits)}")
print(f"Files         : {len(files)}")
print(f"Labels        : {len(labels)}")

# ============================================
# 2. CONVERT DATES
# ============================================

prs["created_at"] = pd.to_datetime(
    prs["created_at"],
    utc=True,
    errors="coerce"
)

commits["commit_date"] = pd.to_datetime(
    commits["commit_date"],
    utc=True,
    errors="coerce"
)

labels["created_at"] = pd.to_datetime(
    labels["created_at"],
    utc=True,
    errors="coerce"
)

# ============================================
# 3. BASIC PR FEATURES
# ============================================

print("\nCreating PR-level features...")

result = pd.DataFrame()

result["pr_number"] = prs["pr_number"]

result["title_length"] = (
    prs["title"]
    .fillna("")
    .astype(str)
    .str.len()
)

result["body_length"] = (
    prs["body"]
    .fillna("")
    .astype(str)
    .str.len()
)

result["title_word_count"] = (
    prs["title"]
    .fillna("")
    .astype(str)
    .str.split()
    .str.len()
)

result["body_word_count"] = (
    prs["body"]
    .fillna("")
    .astype(str)
    .str.split()
    .str.len()
)

result["is_draft"] = (
    prs["draft"]
    .fillna(False)
    .astype(bool)
)

# ============================================
# 4. PREPARE COMMIT DATA
# ============================================

print("Filtering commits to first 24 hours...")

# Keep only commits belonging to known PRs
commits = commits[
    commits["pr_number"].isin(
        prs["pr_number"]
    )
].copy()

# Merge PR creation time into commits
commit_pr_times = prs[
    ["pr_number", "created_at"]
].copy()

commit_pr_times = commit_pr_times.rename(
    columns={
        "created_at": "pr_created_at"
    }
)

commits = commits.merge(
    commit_pr_times,
    on="pr_number",
    how="left"
)

# Time elapsed since PR creation
commits["hours_after_creation"] = (
    commits["commit_date"]
    - commits["pr_created_at"]
).dt.total_seconds() / 3600

# Only commits created between
# PR creation and 24 hours later
early_commits = commits[
    (commits["hours_after_creation"] >= 0)
    & (commits["hours_after_creation"] <= 24)
].copy()

print(
    f"Commits inside first 24h: "
    f"{len(early_commits)}"
)

# ============================================
# 5. COMMIT FEATURES
# ============================================

commit_features = (
    early_commits
    .groupby("pr_number")
    .agg(
        commits_24h=(
            "commit_sha",
            "nunique"
        ),
        commit_authors_24h=(
            "author",
            "nunique"
        )
    )
    .reset_index()
)

# ============================================
# 6. PREPARE FILE DATA
# ============================================

print("Creating 24-hour file-change features...")

files = files.merge(
    early_commits[
        [
            "commit_sha",
            "pr_number"
        ]
    ],
    on="commit_sha",
    how="inner"
)

# Avoid duplicate PR number columns
if "pr_number_x" in files.columns:
    files["pr_number"] = files["pr_number_x"]

# ============================================
# 7. FILE-CHANGE FEATURES
# ============================================

file_features = (
    files
    .groupby("pr_number")
    .agg(
        files_changed_24h=(
            "file_name",
            "nunique"
        ),
        additions_24h=(
            "additions",
            "sum"
        ),
        deletions_24h=(
            "deletions",
            "sum"
        ),
        total_changes_24h=(
            "changes",
            "sum"
        )
    )
    .reset_index()
)

# ============================================
# 8. MERGE EARLY FEATURES
# ============================================

result = result.merge(
    commit_features,
    on="pr_number",
    how="left"
)

result = result.merge(
    file_features,
    on="pr_number",
    how="left"
)

# ============================================
# 9. FILL EARLY ACTIVITY VALUES
# ============================================

activity_columns = [
    "commits_24h",
    "commit_authors_24h",
    "files_changed_24h",
    "additions_24h",
    "deletions_24h",
    "total_changes_24h"
]

for column in activity_columns:
    result[column] = (
        pd.to_numeric(
            result[column],
            errors="coerce"
        )
        .fillna(0)
    )

# ============================================
# 10. DERIVED 24-HOUR FEATURES
# ============================================

result["changes_per_commit_24h"] = np.where(
    result["commits_24h"] > 0,
    result["total_changes_24h"]
    / result["commits_24h"],
    0
)

result["files_per_commit_24h"] = np.where(
    result["commits_24h"] > 0,
    result["files_changed_24h"]
    / result["commits_24h"],
    0
)

result["deletion_ratio_24h"] = np.where(
    result["total_changes_24h"] > 0,
    result["deletions_24h"]
    / result["total_changes_24h"],
    0
)

result["has_commit_activity_24h"] = (
    result["commits_24h"] > 0
).astype(int)

result["has_file_activity_24h"] = (
    result["files_changed_24h"] > 0
).astype(int)

# ============================================
# 11. MERGE TARGET LABEL
# ============================================

target = labels[
    [
        "pr_number",
        "bottleneck_label"
    ]
].copy()

result = result.merge(
    target,
    on="pr_number",
    how="left"
)

# ============================================
# 12. REMOVE CENSORED PRs
# ============================================
# Recent PRs that have not existed for more
# than 7 days do not have a reliable target.

before = len(result)

result = result[
    result["bottleneck_label"].notna()
].copy()

after = len(result)

print(
    f"\nRemoved censored PRs: "
    f"{before - after}"
)

# Convert target to integer
result["bottleneck_label"] = (
    result["bottleneck_label"]
    .astype(int)
)

# ============================================
# 13. CHECK FOR DATA PROBLEMS
# ============================================

print("\n" + "=" * 60)
print("FEATURE DATASET SUMMARY")
print("=" * 60)

print(f"Rows        : {len(result)}")
print(f"Columns     : {len(result.columns)}")

print(
    f"Duplicate rows : "
    f"{result.duplicated().sum()}"
)

print(
    f"Duplicate PRs  : "
    f"{result['pr_number'].duplicated().sum()}"
)

print("\nTarget distribution:")

print(
    result["bottleneck_label"]
    .value_counts()
)

print("\nMissing values:")

missing = result.isna().sum()

print(
    missing[
        missing > 0
    ]
)

# ============================================
# 14. CHECK NEGATIVE VALUES
# ============================================

numeric_columns = result.select_dtypes(
    include=np.number
).columns

negative_counts = (
    result[numeric_columns] < 0
).sum()

negative_counts = negative_counts[
    negative_counts > 0
]

print("\nNegative-value check:")

if len(negative_counts) == 0:
    print("No negative values found.")
else:
    print(negative_counts)

# ============================================
# 15. SAVE
# ============================================

result.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n" + "=" * 60)
print("24-HOUR PREDICTION FEATURES CREATED")
print("=" * 60)

print("Saved to:")
print(OUTPUT_FILE)

print("\nFeatures created:")

for column in result.columns:
    print(f" - {column}")

print("=" * 60)