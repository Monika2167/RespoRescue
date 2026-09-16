import pandas as pd

# Load datasets
issue_pr_commit = pd.read_csv(
    "data/issue_pr_commit_relationships.csv"
)

commits = pd.read_csv(
    "data/commits.csv"
)

files = pd.read_csv(
    "data/files.csv"
)

# Get commits belonging to the connected PRs
connected_prs = set(
    issue_pr_commit.loc[
        issue_pr_commit["has_commits"] == True,
        "pr_number"
    ].astype(int)
)

connected_commits = commits[
    commits["pr_number"].astype(int).isin(connected_prs)
]

# Check which commits have file records
file_commits = set(
    files["commit_sha"].dropna().astype(str)
)

connected_commits = connected_commits.copy()

connected_commits["has_files"] = (
    connected_commits["commit_sha"]
    .astype(str)
    .isin(file_commits)
)

commits_with_files = connected_commits["has_files"].sum()

print("\n==============================")
print("Commit → File Check")
print("==============================")

print("Connected PRs:", len(connected_prs))
print("Commits from connected PRs:", len(connected_commits))
print("Commits with file records:", commits_with_files)
print(
    "Commits without file records:",
    len(connected_commits) - commits_with_files
)

# Save result
connected_commits.to_csv(
    "data/commit_file_relationships.csv",
    index=False
)

print("\nSaved to: data/commit_file_relationships.csv")