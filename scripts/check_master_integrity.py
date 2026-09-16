import pandas as pd

# ==========================================
# 1. Load datasets
# ==========================================

master = pd.read_csv(
    "data/processed/master_relationships_clean.csv"
)

issue_pr = pd.read_csv(
    "data/issue_pr_relationships.csv"
)

commits = pd.read_csv(
    "data/processed/commits_clean.csv"
)

files = pd.read_csv(
    "data/processed/files_clean.csv"
)

print("========================================")
print("MASTER RELATIONSHIP INTEGRITY CHECK")
print("========================================")

# ==========================================
# 2. Basic information
# ==========================================

print("\nMaster dataset shape:", master.shape)

print("Unique Issues:", master["issue_number"].nunique())
print("Unique PRs:", master["pr_number"].nunique())

print(
    "Unique Commits:",
    master["commit_sha"].dropna().nunique()
)

print(
    "Unique Files:",
    master["file_name"].dropna().nunique()
)

# ==========================================
# 3. Issue → PR
# ==========================================

issue_pr["issue_number"] = issue_pr[
    "issue_number"
].astype(int)

issue_pr["pr_number"] = issue_pr[
    "pr_number"
].astype(int)

print("\n========================================")
print("ISSUE → PR CHECK")
print("========================================")

print(
    "Total Issue → PR relationships:",
    len(issue_pr)
)

print(
    "Unique Issues connected:",
    issue_pr["issue_number"].nunique()
)

print(
    "Unique PRs connected:",
    issue_pr["pr_number"].nunique()
)

# ==========================================
# 4. PR → Commit
# ==========================================

commits["pr_number"] = commits[
    "pr_number"
].astype(int)

commit_prs = set(
    commits["pr_number"].unique()
)

issue_pr["has_commit"] = (
    issue_pr["pr_number"].isin(commit_prs)
)

print("\n========================================")
print("PR → COMMIT CHECK")
print("========================================")

print(
    "PRs with commits:",
    issue_pr["has_commit"].sum()
)

print(
    "PRs without commits:",
    (~issue_pr["has_commit"]).sum()
)

# ==========================================
# 5. Commit → File
# ==========================================

files["commit_sha"] = (
    files["commit_sha"]
    .astype(str)
    .str.strip()
)

commit_sha_set = set(
    files["commit_sha"].unique()
)

commits["has_files"] = (
    commits["commit_sha"]
    .astype(str)
    .isin(commit_sha_set)
)

print("\n========================================")
print("COMMIT → FILE CHECK")
print("========================================")

print(
    "Commits with files:",
    commits["has_files"].sum()
)

print(
    "Commits without files:",
    (~commits["has_files"]).sum()
)

# ==========================================
# 6. Complete Issue → PR → Commit → File
# ==========================================

# PRs that have at least one commit
pr_with_commit = set(
    commits.loc[
        commits["has_files"] == True,
        "pr_number"
    ].unique()
)

# Issue → PR relationships where
# PR has commits represented by files
complete_issue_pr = issue_pr[
    issue_pr["pr_number"].isin(pr_with_commit)
]

print("\n========================================")
print("COMPLETE CHAIN CHECK")
print("========================================")

print(
    "Complete Issue → PR → Commit → File relationships:",
    len(complete_issue_pr)
)

print(
    "Issues with complete chain:",
    complete_issue_pr["issue_number"].nunique()
)

print(
    "PRs with complete chain:",
    complete_issue_pr["pr_number"].nunique()
)

# ==========================================
# 7. Broken chains
# ==========================================

broken_issue_pr = issue_pr[
    ~issue_pr["pr_number"].isin(pr_with_commit)
]

print("\n========================================")
print("BROKEN CHAIN CHECK")
print("========================================")

print(
    "Issue → PR links without complete chain:",
    len(broken_issue_pr)
)

# ==========================================
# 8. Missing values in master
# ==========================================

print("\n========================================")
print("MASTER MISSING VALUE CHECK")
print("========================================")

print(
    master.isnull().sum()
)

# ==========================================
# 9. Save integrity result
# ==========================================

complete_issue_pr.to_csv(
    "data/processed/complete_relationships.csv",
    index=False
)

broken_issue_pr.to_csv(
    "data/processed/broken_relationships.csv",
    index=False
)

print("\n========================================")
print("INTEGRITY CHECK COMPLETED")
print("========================================")

print(
    "Complete relationships saved to:",
    "data/processed/complete_relationships.csv"
)

print(
    "Broken relationships saved to:",
    "data/processed/broken_relationships.csv"
)