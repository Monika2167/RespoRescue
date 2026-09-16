import pandas as pd
from pathlib import Path

# ==========================================
# PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

COMMITS_PATH = (
    BASE_DIR
    / "data"
    / "preprocessed"
    / "commits_preprocessed.csv"
)

FILES_PATH = (
    BASE_DIR
    / "data"
    / "preprocessed"
    / "files_preprocessed.csv"
)

OUTPUT_DIR = BASE_DIR / "data" / "features"
OUTPUT_PATH = OUTPUT_DIR / "pr_code_change_features.csv"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ==========================================
# LOAD DATA
# ==========================================

print("=" * 60)
print("CREATING CODE-CHANGE FEATURES")
print("=" * 60)

commits = pd.read_csv(COMMITS_PATH)
files = pd.read_csv(FILES_PATH)

print("\nCommits loaded :", len(commits))
print("File records   :", len(files))


# ==========================================
# COMMIT-LEVEL AGGREGATION
# ==========================================

commit_features = (
    commits
    .groupby("pr_number")
    .agg(
        commits_count=("commit_sha", "nunique"),
        commit_authors=("author", "nunique")
    )
    .reset_index()
)


# ==========================================
# FILE-LEVEL AGGREGATION
# ==========================================

file_features = (
    files
    .groupby("pr_number")
    .agg(
        files_changed=("file_name", "nunique"),
        additions=("additions", "sum"),
        deletions=("deletions", "sum"),
        total_changes=("changes", "sum"),
        max_file_changes=("changes", "max"),
        avg_file_changes=("changes", "mean")
    )
    .reset_index()
)


# ==========================================
# FILE STATUS COUNTS
# ==========================================

status_counts = (
    pd.crosstab(
        files["pr_number"],
        files["status"]
    )
    .reset_index()
)

# Rename status columns safely
status_counts = status_counts.rename(
    columns={
        "added": "files_added",
        "modified": "files_modified",
        "removed": "files_removed",
        "renamed": "files_renamed"
    }
)


# ==========================================
# MERGE FEATURES
# ==========================================

features = commit_features.merge(
    file_features,
    on="pr_number",
    how="outer"
)

features = features.merge(
    status_counts,
    on="pr_number",
    how="left"
)


# ==========================================
# FILL MISSING AGGREGATES
# ==========================================

numeric_columns = [
    "commits_count",
    "commit_authors",
    "files_changed",
    "additions",
    "deletions",
    "total_changes",
    "max_file_changes",
    "avg_file_changes",
    "files_added",
    "files_modified",
    "files_removed",
    "files_renamed"
]

for col in numeric_columns:

    if col not in features.columns:
        features[col] = 0

    features[col] = pd.to_numeric(
        features[col],
        errors="coerce"
    ).fillna(0)


# ==========================================
# CODE CHURN RATIO
# ==========================================

features["deletion_ratio"] = (
    features["deletions"]
    / features["total_changes"].replace(0, pd.NA)
)

features["deletion_ratio"] = (
    features["deletion_ratio"]
    .fillna(0)
)


# ==========================================
# CHANGE INTENSITY
# ==========================================

features["changes_per_commit"] = (
    features["total_changes"]
    / features["commits_count"].replace(0, pd.NA)
)

features["changes_per_commit"] = (
    features["changes_per_commit"]
    .fillna(0)
)


# ==========================================
# FILES PER COMMIT
# ==========================================

features["files_per_commit"] = (
    features["files_changed"]
    / features["commits_count"].replace(0, pd.NA)
)

features["files_per_commit"] = (
    features["files_per_commit"]
    .fillna(0)
)


# ==========================================
# DEVELOPER INVOLVEMENT
# ==========================================

features["developers_involved"] = (
    features["commit_authors"]
)


# ==========================================
# CLEAN NUMERICAL VALUES
# ==========================================

for col in features.columns:

    if col != "pr_number":

        features[col] = pd.to_numeric(
            features[col],
            errors="coerce"
        ).fillna(0)

        features[col] = features[col].clip(
            lower=0
        )


# ==========================================
# SAVE
# ==========================================

features.to_csv(
    OUTPUT_PATH,
    index=False
)


# ==========================================
# SUMMARY
# ==========================================

print("\n" + "=" * 60)
print("CODE-CHANGE FEATURE ENGINEERING COMPLETED")
print("=" * 60)

print("\nPRs represented:", len(features))
print("Columns:", len(features.columns))

print("\nFeatures created:")

for col in features.columns:
    print("  ✓", col)

print("\nSaved to:")
print(OUTPUT_PATH)