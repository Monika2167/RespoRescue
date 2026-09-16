import pandas as pd
from pathlib import Path

# -----------------------------
# Paths
# -----------------------------
BASE_DIR = Path(__file__).resolve().parents[1]

COMMITS_FILE = BASE_DIR / "data" / "cleaned" / "commits_clean.csv"
PRS_FILE = BASE_DIR / "data" / "cleaned" / "pull_requests_clean.csv"
FILES_FILE = BASE_DIR / "data" / "cleaned" / "files_clean.csv"

OUTPUT_DIR = BASE_DIR / "data" / "graph"
OUTPUT_FILE = OUTPUT_DIR / "temporal_features.csv"

# -----------------------------
# Load data
# -----------------------------
commits = pd.read_csv(COMMITS_FILE)
prs = pd.read_csv(PRS_FILE)
files = pd.read_csv(FILES_FILE)

print("Datasets loaded successfully.")

# -----------------------------
# Convert timestamps
# -----------------------------
commits["commit_date"] = pd.to_datetime(
    commits["commit_date"], errors="coerce"
)

prs["created_at"] = pd.to_datetime(
    prs["created_at"], errors="coerce"
)

files = files.dropna(subset=["commit_sha", "file_name"])

# -----------------------------
# Commit temporal features
# -----------------------------
commit_data = commits.dropna(
    subset=["commit_date"]
).copy()

commit_data["week"] = (
    commit_data["commit_date"]
    .dt.to_period("W")
    .astype(str)
)

commits_per_week = (
    commit_data
    .groupby("week")
    .agg(
        commits_per_week=("commit_sha", "nunique"),
        active_developers=("author", "nunique")
    )
    .reset_index()
)

# -----------------------------
# PR temporal features
# -----------------------------
pr_data = prs.dropna(
    subset=["created_at"]
).copy()

pr_data["week"] = (
    pr_data["created_at"]
    .dt.to_period("W")
    .astype(str)
)

prs_per_week = (
    pr_data
    .groupby("week")
    .agg(
        prs_per_week=("pr_number", "nunique"),
        pr_authors=("author", "nunique")
    )
    .reset_index()
)

# -----------------------------
# Files changed per week
# -----------------------------
file_dates = files.merge(
    commits[["commit_sha", "commit_date"]],
    on="commit_sha",
    how="inner"
)

file_dates["commit_date"] = pd.to_datetime(
    file_dates["commit_date"],
    errors="coerce"
)

file_dates = file_dates.dropna(
    subset=["commit_date"]
)

file_dates["week"] = (
    file_dates["commit_date"]
    .dt.to_period("W")
    .astype(str)
)

files_per_week = (
    file_dates
    .groupby("week")
    .agg(
        files_changed_per_week=("file_name", "nunique")
    )
    .reset_index()
)

# -----------------------------
# Merge weekly features
# -----------------------------
temporal_features = commits_per_week.merge(
    prs_per_week,
    on="week",
    how="outer"
)

temporal_features = temporal_features.merge(
    files_per_week,
    on="week",
    how="outer"
)

temporal_features = temporal_features.sort_values(
    "week"
).reset_index(drop=True)

# -----------------------------
# Fill missing values
# -----------------------------
numeric_columns = [
    "commits_per_week",
    "active_developers",
    "prs_per_week",
    "pr_authors",
    "files_changed_per_week"
]

for column in numeric_columns:
    temporal_features[column] = (
        temporal_features[column]
        .fillna(0)
        .astype(int)
    )

# -----------------------------
# Save output
# -----------------------------
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

temporal_features.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nTemporal analysis completed!")
print("Weeks analyzed:", len(temporal_features))

print("\nOutput file:")
print(OUTPUT_FILE)

print("\nSample:")
print(temporal_features.head(10).to_string(index=False))