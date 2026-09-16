import pandas as pd

# Load datasets
issue_pr = pd.read_csv("data/issue_pr_relationships.csv")
commits = pd.read_csv("data/commits.csv")

print("Issue → PR relationships:", len(issue_pr))
print("Total commits:", len(commits))

# PR numbers that have commits
commit_prs = set(commits["pr_number"].dropna().astype(int))

# Check how many Issue → PR relationships connect to commits
issue_pr = issue_pr.copy()

issue_pr["pr_number"] = issue_pr["pr_number"].astype(int)

issue_pr["has_commits"] = issue_pr["pr_number"].isin(commit_prs)

connected = issue_pr["has_commits"].sum()

print("\n==============================")
print("Issue → PR → Commit Check")
print("==============================")
print("Issue → PR relationships:", len(issue_pr))
print("PRs connected to commits:", connected)
print("PRs without commits:", len(issue_pr) - connected)

# Save verification result
issue_pr.to_csv(
    "data/issue_pr_commit_relationships.csv",
    index=False
)

print("\nSaved to: data/issue_pr_commit_relationships.csv")