import pandas as pd
from pathlib import Path


# -----------------------------
# Paths
# -----------------------------
DATA_DIR = Path("data/cleaned")
OUTPUT_DIR = Path("data/graph")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# -----------------------------
# Load datasets
# -----------------------------
commits = pd.read_csv(
    DATA_DIR / "commits_clean.csv",
    dtype=str
)

files = pd.read_csv(
    DATA_DIR / "files_clean.csv",
    dtype=str
)

print("Datasets loaded successfully.")
print(f"Commits: {len(commits)}")
print(f"File changes: {len(files)}")


# -----------------------------
# Developer -> File relationship
# -----------------------------
developer_commits = commits[
    ["commit_sha", "author"]
].dropna()

commit_files = files[
    ["commit_sha", "file_name"]
].dropna()


developer_file = developer_commits.merge(
    commit_files,
    on="commit_sha",
    how="inner"
)


# Remove duplicate developer-file relationships
developer_file = developer_file.drop_duplicates(
    subset=["author", "file_name"]
)


# -----------------------------
# Developer-level features
# -----------------------------

developer_features = (
    developer_file
    .groupby("author")
    .agg(
        files_per_developer=("file_name", "nunique")
    )
    .reset_index()
    .rename(columns={"author": "developer"})
)


# Count commits per developer
commit_counts = (
    commits
    .dropna(subset=["author"])
    .groupby("author")
    .size()
    .reset_index(name="commits_per_developer")
    .rename(columns={"author": "developer"})
)


developer_features = developer_features.merge(
    commit_counts,
    on="developer",
    how="left"
)


# -----------------------------
# File-level features
# -----------------------------

file_features = (
    developer_file
    .groupby("file_name")
    .agg(
        unique_developers_per_file=("author", "nunique")
    )
    .reset_index()
)


# -----------------------------
# Single-contributor flag
# -----------------------------

file_features["single_contributor_flag"] = (
    file_features["unique_developers_per_file"] == 1
).astype(int)


# -----------------------------
# Save developer-file relationships
# -----------------------------

developer_file.to_csv(
    OUTPUT_DIR / "developer_file_relationships.csv",
    index=False
)


# -----------------------------
# Save developer features
# -----------------------------

developer_features.to_csv(
    OUTPUT_DIR / "developer_features.csv",
    index=False
)


# -----------------------------
# Save file features
# -----------------------------

file_features.to_csv(
    OUTPUT_DIR / "file_features.csv",
    index=False
)


# -----------------------------
# Summary
# -----------------------------

print("\nDeveloper-file graph analysis completed!")

print(
    f"Unique developer-file relationships: "
    f"{len(developer_file)}"
)

print(
    f"Unique developers: "
    f"{developer_file['author'].nunique()}"
)

print(
    f"Unique files: "
    f"{developer_file['file_name'].nunique()}"
)

print(
    f"Files with single contributor: "
    f"{file_features['single_contributor_flag'].sum()}"
)

print("\nOutput files:")
print(OUTPUT_DIR / "developer_file_relationships.csv")
print(OUTPUT_DIR / "developer_features.csv")
print(OUTPUT_DIR / "file_features.csv")