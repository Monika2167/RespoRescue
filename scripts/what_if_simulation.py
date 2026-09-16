import pandas as pd
from pathlib import Path

# -----------------------------
# Paths
# -----------------------------
BASE_DIR = Path(__file__).resolve().parents[1]

COMMITS_FILE = BASE_DIR / "data" / "cleaned" / "commits_clean.csv"
FILES_FILE = BASE_DIR / "data" / "cleaned" / "files_clean.csv"

OUTPUT_DIR = BASE_DIR / "data" / "graph"
OUTPUT_FILE = OUTPUT_DIR / "what_if_results.csv"

# -----------------------------
# Load data
# -----------------------------
commits = pd.read_csv(COMMITS_FILE)
files = pd.read_csv(FILES_FILE)

print("Datasets loaded successfully.")

# -----------------------------
# Join developer -> file
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
# Developer-file contribution count
# -----------------------------
contribution = (
    developer_files
    .groupby(["file_name", "author"])
    .size()
    .reset_index(name="commit_count")
)

# -----------------------------
# File totals
# -----------------------------
file_totals = (
    contribution
    .groupby("file_name")["commit_count"]
    .sum()
    .rename("total_commits")
)

contribution = contribution.merge(
    file_totals,
    on="file_name",
    how="left"
)

# -----------------------------
# Developer share
# -----------------------------
contribution["developer_share"] = (
    contribution["commit_count"]
    / contribution["total_commits"]
)

# -----------------------------
# Dominant developer per file
# -----------------------------
dominant = (
    contribution
    .sort_values(
        ["file_name", "developer_share"],
        ascending=[True, False]
    )
    .drop_duplicates("file_name")
)

dominant = dominant[
    [
        "file_name",
        "author",
        "developer_share",
        "total_commits"
    ]
].rename(
    columns={
        "author": "dominant_developer",
        "developer_share": "dominant_developer_share"
    }
)

# -----------------------------
# Number of contributors
# -----------------------------
contributors = (
    contribution
    .groupby("file_name")["author"]
    .nunique()
    .rename("unique_developers")
)

dominant = dominant.merge(
    contributors,
    on="file_name",
    how="left"
)

# -----------------------------
# What-if simulation
# -----------------------------
dominant["files_losing_dominant_contributor"] = (
    dominant["dominant_developer_share"] >= 0.50
).astype(int)

dominant["files_with_no_remaining_contributor"] = (
    dominant["unique_developers"] == 1
).astype(int)

# Approximate remaining contribution after dominant developer removal
dominant["remaining_contributor_share"] = (
    1 - dominant["dominant_developer_share"]
)

# Risk flag based on concentration
dominant["high_concentration_flag"] = (
    dominant["dominant_developer_share"] >= 0.75
).astype(int)

# -----------------------------
# Save results
# -----------------------------
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

dominant.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nWhat-if simulation completed!")

print(
    "Files analyzed:",
    len(dominant)
)

print(
    "Files losing dominant contributor:",
    dominant["files_losing_dominant_contributor"].sum()
)

print(
    "Files with no remaining contributor:",
    dominant["files_with_no_remaining_contributor"].sum()
)

print(
    "Highly concentrated files:",
    dominant["high_concentration_flag"].sum()
)

print("\nOutput file:")
print(OUTPUT_FILE)

print("\nSample results:")
print(dominant.head(10).to_string(index=False))