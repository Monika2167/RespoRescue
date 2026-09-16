import pandas as pd
from pathlib import Path

# -----------------------------
# Paths
# -----------------------------
BASE_DIR = Path(__file__).resolve().parents[1]

COMMITS_FILE = BASE_DIR / "data" / "cleaned" / "commits_clean.csv"
FILES_FILE = BASE_DIR / "data" / "cleaned" / "files_clean.csv"

OUTPUT_DIR = BASE_DIR / "data" / "graph"
OUTPUT_FILE = OUTPUT_DIR / "knowledge_concentration.csv"

# -----------------------------
# Load data
# -----------------------------
commits = pd.read_csv(COMMITS_FILE)
files = pd.read_csv(FILES_FILE)

print("Datasets loaded successfully.")
print("Commits:", len(commits))
print("File changes:", len(files))

# -----------------------------
# Join commits with files
# -----------------------------
developer_files = files.merge(
    commits[["commit_sha", "author"]],
    on="commit_sha",
    how="inner"
)

developer_files = developer_files.dropna(
    subset=["author", "file_name"]
)

# -----------------------------
# Total commits per developer
# -----------------------------
commits_per_developer = (
    commits.dropna(subset=["author"])
    .groupby("author")["commit_sha"]
    .nunique()
    .rename("commits_per_developer")
)

# -----------------------------
# Files per developer
# -----------------------------
files_per_developer = (
    developer_files
    .groupby("author")["file_name"]
    .nunique()
    .rename("files_per_developer")
)

# -----------------------------
# Developer contribution count
# -----------------------------
developer_file_commits = (
    developer_files
    .groupby(["file_name", "author"])
    .size()
    .reset_index(name="developer_commit_count")
)

# -----------------------------
# File-level concentration
# -----------------------------
file_totals = (
    developer_file_commits
    .groupby("file_name")["developer_commit_count"]
    .sum()
    .rename("total_file_commits")
)

developer_file_commits = developer_file_commits.merge(
    file_totals,
    on="file_name",
    how="left"
)

# Developer's share of file contributions
developer_file_commits["developer_share"] = (
    developer_file_commits["developer_commit_count"]
    / developer_file_commits["total_file_commits"]
)

# -----------------------------
# Calculate file-level metrics
# -----------------------------
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

# Single contributor flag
file_metrics["single_contributor_flag"] = (
    file_metrics["unique_developers_per_file"] == 1
).astype(int)

# -----------------------------
# Contributor concentration
# -----------------------------
file_metrics["contributor_concentration"] = (
    file_metrics["dominant_developer_share"]
)

# -----------------------------
# Merge developer-level information
# -----------------------------
developer_summary = (
    developer_file_commits
    .groupby("author")
    .agg(
        files_per_developer=("file_name", "nunique")
    )
    .reset_index()
    .rename(columns={"author": "developer"})
)

developer_summary = developer_summary.merge(
    commits_per_developer.reset_index().rename(
        columns={"author": "developer"}
    ),
    on="developer",
    how="left"
)

# -----------------------------
# Add dominant developer
# -----------------------------
dominant_developers = (
    developer_file_commits
    .sort_values(
        ["file_name", "developer_share"],
        ascending=[True, False]
    )
    .drop_duplicates("file_name")
    [["file_name", "author"]]
    .rename(columns={"author": "dominant_developer"})
)

file_metrics = file_metrics.merge(
    dominant_developers,
    on="file_name",
    how="left"
)

# -----------------------------
# Save output
# -----------------------------
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

file_metrics.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nKnowledge concentration analysis completed!")

print("Files analyzed:", len(file_metrics))
print(
    "Single-contributor files:",
    file_metrics["single_contributor_flag"].sum()
)

print("\nOutput file:")
print(OUTPUT_FILE)