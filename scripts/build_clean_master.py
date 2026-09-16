import pandas as pd
import os

# ==========================================
# 1. File paths
# ==========================================

issues_path = "data/processed/issues_clean.csv"
prs_path = "data/processed/pull_requests_clean.csv"
commits_path = "data/processed/commits_clean.csv"
files_path = "data/processed/files_clean.csv"

output_dir = "data/processed"
output_path = os.path.join(
    output_dir,
    "master_relationships_clean.csv"
)

os.makedirs(output_dir, exist_ok=True)

# ==========================================
# 2. Load cleaned datasets
# ==========================================

issues = pd.read_csv(issues_path)
prs = pd.read_csv(prs_path)
commits = pd.read_csv(commits_path)
files = pd.read_csv(files_path)

print("================================")
print("BUILDING CLEAN MASTER DATASET")
print("================================")

print("\nLoaded datasets:")
print("Issues:", issues.shape)
print("Pull Requests:", prs.shape)
print("Commits:", commits.shape)
print("Files:", files.shape)

# ==========================================
# 3. Load Issue → PR relationships
# ==========================================

relationship_path = "data/issue_pr_relationships.csv"

issue_pr = pd.read_csv(relationship_path)

print("\nIssue → PR relationships:", issue_pr.shape)

# ==========================================
# 4. Select useful columns
# ==========================================

issues = issues[
    [
        "issue_number",
        "title",
        "state",
        "created_at",
        "closed_at",
        "author"
    ]
]

prs = prs[
    [
        "pr_number",
        "title",
        "state",
        "created_at",
        "updated_at",
        "closed_at",
        "merged_at",
        "author",
        "draft"
    ]
]

commits = commits[
    [
        "pr_number",
        "commit_sha",
        "commit_message",
        "author",
        "commit_date"
    ]
]

files = files[
    [
        "commit_sha",
        "file_name",
        "status",
        "additions",
        "deletions",
        "changes"
    ]
]

# ==========================================
# 5. Make sure relationship IDs are integers
# ==========================================

issue_pr["issue_number"] = pd.to_numeric(
    issue_pr["issue_number"],
    errors="coerce"
)

issue_pr["pr_number"] = pd.to_numeric(
    issue_pr["pr_number"],
    errors="coerce"
)

issue_pr = issue_pr.dropna(
    subset=["issue_number", "pr_number"]
)

issue_pr["issue_number"] = issue_pr["issue_number"].astype(int)
issue_pr["pr_number"] = issue_pr["pr_number"].astype(int)

prs["pr_number"] = prs["pr_number"].astype(int)
commits["pr_number"] = commits["pr_number"].astype(int)

# ==========================================
# 6. Issue → PR
# ==========================================

master = issue_pr.merge(
    issues,
    on="issue_number",
    how="left"
)

print("\nAfter Issue → PR merge:", master.shape)

# ==========================================
# 7. PR → Commit
# ==========================================

master = master.merge(
    commits,
    on="pr_number",
    how="left"
)

print("After PR → Commit merge:", master.shape)

# ==========================================
# 8. Commit → File
# ==========================================

master = master.merge(
    files,
    on="commit_sha",
    how="left"
)

print("After Commit → File merge:", master.shape)

# ==========================================
# 9. Remove exact duplicate rows
# ==========================================

before_duplicates = len(master)

master = master.drop_duplicates()

after_duplicates = len(master)

print(
    "\nDuplicate rows removed:",
    before_duplicates - after_duplicates
)

# ==========================================
# 10. Convert dates
# ==========================================

date_columns = [
    "created_at",
    "closed_at",
    "updated_at",
    "merged_at",
    "commit_date"
]

for column in date_columns:

    if column in master.columns:

        master[column] = pd.to_datetime(
            master[column],
            errors="coerce",
            utc=True
        )

# ==========================================
# 11. Final validation
# ==========================================

print("\n================================")
print("MASTER DATASET VALIDATION")
print("================================")

print("\nFinal shape:", master.shape)

print("\nUnique Issues:",
      master["issue_number"].nunique())

print("Unique PRs:",
      master["pr_number"].nunique())

print("Unique Commits:",
      master["commit_sha"].nunique())

print("Unique Files:",
      master["file_name"].nunique())

print("\nMissing values:")
print(master.isnull().sum())

print("\nDuplicate rows:",
      master.duplicated().sum())

# ==========================================
# 12. Save
# ==========================================

master.to_csv(
    output_path,
    index=False
)

print("\n================================")
print("CLEAN MASTER DATASET CREATED")
print("================================")

print("Saved to:")
print(output_path)

print("\nColumns:")
print(list(master.columns))