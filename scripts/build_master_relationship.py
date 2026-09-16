import pandas as pd

# Load datasets
issues = pd.read_csv("data/issues.csv")
issue_pr = pd.read_csv("data/issue_pr_relationships.csv")
commits = pd.read_csv("data/commits.csv")
files = pd.read_csv("data/files.csv")

# Keep only the columns we need
issues = issues[
    ["issue_number", "title", "state", "created_at", "closed_at", "author"]
]

issue_pr = issue_pr[
    ["issue_number", "pr_number"]
]

commits = commits[
    ["pr_number", "commit_sha", "commit_message", "author", "commit_date"]
]

files = files[
    ["commit_sha", "file_name", "status",
     "additions", "deletions", "changes"]
]

# Make IDs consistent
issue_pr["issue_number"] = issue_pr["issue_number"].astype(int)
issue_pr["pr_number"] = issue_pr["pr_number"].astype(int)

commits["pr_number"] = commits["pr_number"].astype(int)

# --------------------------------------------------
# Issue → PR
# --------------------------------------------------

master = issue_pr.merge(
    issues,
    on="issue_number",
    how="left"
)

# --------------------------------------------------
# PR → Commit
# --------------------------------------------------

master = master.merge(
    commits,
    on="pr_number",
    how="left",
    suffixes=("_pr", "_commit")
)

# --------------------------------------------------
# Commit → File
# --------------------------------------------------

master = master.merge(
    files,
    on="commit_sha",
    how="left"
)

# Remove exact duplicate rows
master = master.drop_duplicates()

# Save master relationship dataset
master.to_csv(
    "data/master_relationships.csv",
    index=False
)

print("\n==============================")
print("Master Relationship Dataset")
print("==============================")

print("Total rows:", len(master))
print("Total columns:", len(master.columns))

print("\nColumns:")
print(list(master.columns))

print("\nUnique Issues:",
      master["issue_number"].nunique())

print("Unique PRs:",
      master["pr_number"].nunique())

print("Unique Commits:",
      master["commit_sha"].nunique())

print("Unique Files:",
      master["file_name"].nunique())

print("\nSaved to:")
print("data/master_relationships.csv")

print("==============================")