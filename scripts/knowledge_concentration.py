import pandas as pd
from pathlib import Path


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

COMMITS_FILE = BASE_DIR / "data" / "cleaned" / "commits_clean.csv"
FILES_FILE = BASE_DIR / "data" / "cleaned" / "files_clean.csv"

OUTPUT_DIR = BASE_DIR / "data" / "graph"
OUTPUT_FILE = OUTPUT_DIR / "knowledge_concentration.csv"


# ---------------------------------------------------------
# Load datasets
# ---------------------------------------------------------
commits = pd.read_csv(COMMITS_FILE)
files = pd.read_csv(FILES_FILE)

print("Datasets loaded successfully.")
print(f"Commits: {len(commits)}")
print(f"File changes: {len(files)}")


# ---------------------------------------------------------
# Select required columns
# ---------------------------------------------------------
commits = commits[
    ["commit_sha", "author"]
].dropna(subset=["commit_sha", "author"])

files = files[
    ["commit_sha", "file_name"]
].dropna(subset=["commit_sha", "file_name"])


# ---------------------------------------------------------
# Connect developers -> commits -> files
# ---------------------------------------------------------
developer_file_data = files.merge(
    commits,
    on="commit_sha",
    how="inner"
)

# Keep one contribution record per
# developer + file + commit
developer_file_data = developer_file_data.drop_duplicates(
    subset=["author", "file_name", "commit_sha"]
)

print(
    f"Developer-file contribution rows: "
    f"{len(developer_file_data)}"
)


# ---------------------------------------------------------
# Developer contribution count per file
# ---------------------------------------------------------
developer_file_commits = (
    developer_file_data
    .groupby(["file_name", "author"])
    .size()
    .reset_index(name="developer_commit_count")
)


# ---------------------------------------------------------
# Total commits for each file
# ---------------------------------------------------------
file_totals = (
    developer_file_commits
    .groupby("file_name")["developer_commit_count"]
    .sum()
    .reset_index(name="total_file_commits")
)


# ---------------------------------------------------------
# Calculate developer contribution share
# ---------------------------------------------------------
developer_file_commits = developer_file_commits.merge(
    file_totals,
    on="file_name",
    how="left"
)

developer_file_commits["developer_share"] = (
    developer_file_commits["developer_commit_count"]
    / developer_file_commits["total_file_commits"]
)


# ---------------------------------------------------------
# File-level knowledge concentration
# ---------------------------------------------------------
file_metrics = (
    developer_file_commits
    .groupby("file_name")
    .agg(
        unique_developers_per_file=("author", "nunique"),
        dominant_developer_share=("developer_share", "max"),
        total_file_commits=("total_file_commits", "first")
    )
    .reset_index()
)


# ---------------------------------------------------------
# Identify dominant developer and their commit count
# ---------------------------------------------------------
dominant_indices = (
    developer_file_commits
    .groupby("file_name")["developer_share"]
    .idxmax()
)

dominant_developers = (
    developer_file_commits
    .loc[
        dominant_indices,
        [
            "file_name",
            "author",
            "developer_commit_count"
        ]
    ]
    .rename(
        columns={
            "author": "dominant_developer",
            "developer_commit_count":
                "dominant_developer_commit_count"
        }
    )
)


# ---------------------------------------------------------
# Combine dominant developer information
# ---------------------------------------------------------
file_metrics = file_metrics.merge(
    dominant_developers,
    on="file_name",
    how="left"
)


# ---------------------------------------------------------
# Single-contributor flag
# ---------------------------------------------------------
file_metrics["single_contributor_flag"] = (
    file_metrics["unique_developers_per_file"] == 1
).astype(int)


# ---------------------------------------------------------
# Contributor concentration
#
# Kept for compatibility with the existing output.
# It represents the share of file commits made by
# the dominant observed contributor.
# ---------------------------------------------------------
file_metrics["contributor_concentration"] = (
    file_metrics["dominant_developer_share"]
)


# ---------------------------------------------------------
# Concentration risk signal
#
# HIGH:
#   dominant share >= 75%
#   AND dominant developer has >= 5 commits
#
# MEDIUM:
#   dominant share >= 50%
#   AND dominant developer has >= 3 commits
#
# LOW:
#   otherwise
#
# This is an analytical signal, NOT proof of failure
# or developer dependency.
# ---------------------------------------------------------
def calculate_risk(row):

    share = row["dominant_developer_share"]
    commits = row["dominant_developer_commit_count"]

    if share >= 0.75 and commits >= 5:
        return "HIGH"

    if share >= 0.50 and commits >= 3:
        return "MEDIUM"

    return "LOW"


file_metrics["concentration_risk_signal"] = (
    file_metrics.apply(calculate_risk, axis=1)
)


# ---------------------------------------------------------
# Final column order
#
# Existing columns are preserved.
# New columns are added only where useful.
# ---------------------------------------------------------
file_metrics = file_metrics[
    [
        "file_name",
        "unique_developers_per_file",
        "dominant_developer_share",
        "total_file_commits",
        "single_contributor_flag",
        "contributor_concentration",
        "dominant_developer",
        "dominant_developer_commit_count",
        "concentration_risk_signal"
    ]
]


# ---------------------------------------------------------
# Validation
# ---------------------------------------------------------
print("\nValidation:")

print(f"Files analysed: {len(file_metrics)}")
print(
    "Missing values:",
    int(file_metrics.isna().sum().sum())
)
print(
    "Duplicate rows:",
    int(file_metrics.duplicated().sum())
)

print("\nRisk signal distribution:")
print(
    file_metrics["concentration_risk_signal"]
    .value_counts()
    .to_string()
)


# ---------------------------------------------------------
# Save output
# ---------------------------------------------------------
OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

file_metrics.to_csv(
    OUTPUT_FILE,
    index=False
)


# ---------------------------------------------------------
# Final summary
# ---------------------------------------------------------
print("\nKnowledge concentration analysis completed!")

print(
    f"Files analysed: "
    f"{len(file_metrics)}"
)

print(
    "Single-contributor files:",
    int(file_metrics["single_contributor_flag"].sum())
)

print("\nOutput file:")
print(OUTPUT_FILE)