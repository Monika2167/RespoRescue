import pandas as pd
import os

# ==========================================
# CONFIGURATION
# ==========================================

DATA_DIR = "data"
CLEAN_DIR = "data/cleaned"

os.makedirs(CLEAN_DIR, exist_ok=True)


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def clean_text_column(df, column):
    """Fill missing text and remove unnecessary whitespace."""
    if column in df.columns:
        df[column] = df[column].fillna("").astype(str).str.strip()

    return df


def clean_date_column(df, column):
    """Convert dates to proper datetime format."""
    if column in df.columns:
        df[column] = pd.to_datetime(
            df[column],
            errors="coerce",
            utc=True
        )

    return df


# ==========================================
# 1. CLEAN ISSUES
# ==========================================

print("\n" + "=" * 60)
print("CLEANING ISSUES")
print("=" * 60)

issues = pd.read_csv(
    os.path.join(DATA_DIR, "issues.csv"),
    low_memory=False
)

print(f"Original rows: {len(issues):,}")

# Remove exact duplicate rows
issues = issues.drop_duplicates()

# Remove duplicate issue numbers
issues = issues.drop_duplicates(
    subset=["issue_number"],
    keep="first"
)

# Text columns
issues = clean_text_column(issues, "title")
issues = clean_text_column(issues, "body")
issues = clean_text_column(issues, "author")
issues = clean_text_column(issues, "labels")
issues = clean_text_column(issues, "state")

# Missing title
issues["title"] = issues["title"].replace(
    "",
    "Untitled issue"
)

# Numeric column
issues["comments_count"] = pd.to_numeric(
    issues["comments_count"],
    errors="coerce"
).fillna(0).astype(int)

# Date columns
for column in [
    "created_at",
    "updated_at",
    "closed_at"
]:
    issues = clean_date_column(issues, column)

# Save
issues.to_csv(
    os.path.join(CLEAN_DIR, "issues_clean.csv"),
    index=False
)

print(f"Cleaned rows : {len(issues):,}")
print("Saved: data/cleaned/issues_clean.csv")


# ==========================================
# 2. CLEAN PULL REQUESTS
# ==========================================

print("\n" + "=" * 60)
print("CLEANING PULL REQUESTS")
print("=" * 60)

prs = pd.read_csv(
    os.path.join(DATA_DIR, "pull_requests.csv"),
    low_memory=False
)

print(f"Original rows: {len(prs):,}")

# Remove exact duplicates
prs = prs.drop_duplicates()

# Remove duplicate PR numbers
prs = prs.drop_duplicates(
    subset=["pr_number"],
    keep="first"
)

# Text columns
prs = clean_text_column(prs, "title")
prs = clean_text_column(prs, "body")
prs = clean_text_column(prs, "author")
prs = clean_text_column(prs, "state")
prs = clean_text_column(prs, "html_url")

# Missing title
prs["title"] = prs["title"].replace(
    "",
    "Untitled pull request"
)

# Date columns
for column in [
    "created_at",
    "updated_at",
    "closed_at",
    "merged_at"
]:
    prs = clean_date_column(prs, column)

# Ensure draft is boolean
prs["draft"] = prs["draft"].fillna(False).astype(bool)

# Save
prs.to_csv(
    os.path.join(CLEAN_DIR, "pull_requests_clean.csv"),
    index=False
)

print(f"Cleaned rows : {len(prs):,}")
print("Saved: data/cleaned/pull_requests_clean.csv")


# ==========================================
# 3. CLEAN COMMITS
# ==========================================

print("\n" + "=" * 60)
print("CLEANING COMMITS")
print("=" * 60)

commits = pd.read_csv(
    os.path.join(DATA_DIR, "commits.csv"),
    low_memory=False
)

print(f"Original rows: {len(commits):,}")

# Remove exact duplicates
commits = commits.drop_duplicates()

# Commit SHA must be unique
commits = commits.drop_duplicates(
    subset=["commit_sha"],
    keep="first"
)

# Text columns
commits = clean_text_column(
    commits,
    "commit_sha"
)

commits = clean_text_column(
    commits,
    "commit_message"
)

commits = clean_text_column(
    commits,
    "author"
)

# Convert PR number
commits["pr_number"] = pd.to_numeric(
    commits["pr_number"],
    errors="coerce"
)

# Date
commits = clean_date_column(
    commits,
    "commit_date"
)

# Save
commits.to_csv(
    os.path.join(CLEAN_DIR, "commits_clean.csv"),
    index=False
)

print(f"Cleaned rows : {len(commits):,}")
print("Saved: data/cleaned/commits_clean.csv")


# ==========================================
# 4. CLEAN FILES
# ==========================================

print("\n" + "=" * 60)
print("CLEANING FILES")
print("=" * 60)

files = pd.read_csv(
    os.path.join(DATA_DIR, "files.csv"),
    low_memory=False
)

print(f"Original rows: {len(files):,}")

# Remove exact duplicates
files = files.drop_duplicates()

# Remove invalid rows without commit SHA
files = files[
    files["commit_sha"].notna()
]

# Text columns
files = clean_text_column(
    files,
    "commit_sha"
)

files = clean_text_column(
    files,
    "file_name"
)

files = clean_text_column(
    files,
    "status"
)

# Numeric columns
for column in [
    "pr_number",
    "additions",
    "deletions",
    "changes"
]:
    files[column] = pd.to_numeric(
        files[column],
        errors="coerce"
    ).fillna(0)

# Convert to integers
files["pr_number"] = files["pr_number"].astype(int)
files["additions"] = files["additions"].astype(int)
files["deletions"] = files["deletions"].astype(int)
files["changes"] = files["changes"].astype(int)

# Prevent impossible negative values
for column in [
    "additions",
    "deletions",
    "changes"
]:
    files.loc[
        files[column] < 0,
        column
    ] = 0

# Save
files.to_csv(
    os.path.join(CLEAN_DIR, "files_clean.csv"),
    index=False
)

print(f"Cleaned rows : {len(files):,}")
print("Saved: data/cleaned/files_clean.csv")


# ==========================================
# FINAL SUMMARY
# ==========================================

print("\n" + "=" * 60)
print("DATA CLEANING COMPLETED SUCCESSFULLY")
print("=" * 60)

print(f"Issues        : {len(issues):,}")
print(f"Pull Requests : {len(prs):,}")
print(f"Commits       : {len(commits):,}")
print(f"Files         : {len(files):,}")

print("\nCleaned files:")
print("data/cleaned/issues_clean.csv")
print("data/cleaned/pull_requests_clean.csv")
print("data/cleaned/commits_clean.csv")
print("data/cleaned/files_clean.csv")

print("\nOriginal datasets were NOT modified.")