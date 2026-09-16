import os
import pandas as pd

# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

CLEANED_DIR = os.path.join(
    BASE_DIR,
    "data",
    "cleaned"
)

PREPROCESSED_DIR = os.path.join(
    BASE_DIR,
    "data",
    "preprocessed"
)

os.makedirs(PREPROCESSED_DIR, exist_ok=True)

# ============================================================
# LOAD CLEANED DATA
# ============================================================

issues = pd.read_csv(
    os.path.join(CLEANED_DIR, "issues_clean.csv")
)

pull_requests = pd.read_csv(
    os.path.join(CLEANED_DIR, "pull_requests_clean.csv")
)

commits = pd.read_csv(
    os.path.join(CLEANED_DIR, "commits_clean.csv")
)

files = pd.read_csv(
    os.path.join(CLEANED_DIR, "files_clean.csv")
)

# ============================================================
# BASIC INFORMATION
# ============================================================

print("\n==============================")
print("LOADED CLEANED DATA")
print("==============================")

print("Issues        :", len(issues))
print("Pull Requests :", len(pull_requests))
print("Commits       :", len(commits))
print("Files         :", len(files))

# ============================================================
# COPY DATA
# ============================================================

issues_p = issues.copy()
pull_requests_p = pull_requests.copy()
commits_p = commits.copy()
files_p = files.copy()

# ============================================================
# TEXT COLUMNS
# ============================================================

# Ensure text columns are strings

issues_p["title"] = (
    issues_p["title"]
    .fillna("")
    .astype(str)
    .str.strip()
)

issues_p["body"] = (
    issues_p["body"]
    .fillna("")
    .astype(str)
    .str.strip()
)

pull_requests_p["title"] = (
    pull_requests_p["title"]
    .fillna("")
    .astype(str)
    .str.strip()
)

pull_requests_p["body"] = (
    pull_requests_p["body"]
    .fillna("")
    .astype(str)
    .str.strip()
)

commits_p["commit_message"] = (
    commits_p["commit_message"]
    .fillna("")
    .astype(str)
    .str.strip()
)

# ============================================================
# DATE/TIME PREPROCESSING
# ============================================================

issue_date_columns = [
    "created_at",
    "updated_at",
    "closed_at"
]

pr_date_columns = [
    "created_at",
    "updated_at",
    "closed_at",
    "merged_at"
]

commit_date_columns = [
    "commit_date"
]

for column in issue_date_columns:
    issues_p[column] = pd.to_datetime(
        issues_p[column],
        errors="coerce",
        utc=True
    )

for column in pr_date_columns:
    pull_requests_p[column] = pd.to_datetime(
        pull_requests_p[column],
        errors="coerce",
        utc=True
    )

for column in commit_date_columns:
    commits_p[column] = pd.to_datetime(
        commits_p[column],
        errors="coerce",
        utc=True
    )

# ============================================================
# NUMERICAL COLUMNS
# ============================================================

issues_p["comments_count"] = pd.to_numeric(
    issues_p["comments_count"],
    errors="coerce"
).fillna(0)

files_p["additions"] = pd.to_numeric(
    files_p["additions"],
    errors="coerce"
).fillna(0)

files_p["deletions"] = pd.to_numeric(
    files_p["deletions"],
    errors="coerce"
).fillna(0)

files_p["changes"] = pd.to_numeric(
    files_p["changes"],
    errors="coerce"
).fillna(0)

# ============================================================
# BOOLEAN
# ============================================================

pull_requests_p["draft"] = (
    pull_requests_p["draft"]
    .astype(bool)
)

# ============================================================
# BASIC NUMERICAL SANITY CHECK
# ============================================================

for column in [
    "comments_count"
]:

    issues_p[column] = issues_p[column].clip(
        lower=0
    )

for column in [
    "additions",
    "deletions",
    "changes"
]:

    files_p[column] = files_p[column].clip(
        lower=0
    )

# ============================================================
# SAVE PREPROCESSED DATA
# ============================================================

issues_p.to_csv(
    os.path.join(
        PREPROCESSED_DIR,
        "issues_preprocessed.csv"
    ),
    index=False
)

pull_requests_p.to_csv(
    os.path.join(
        PREPROCESSED_DIR,
        "pull_requests_preprocessed.csv"
    ),
    index=False
)

commits_p.to_csv(
    os.path.join(
        PREPROCESSED_DIR,
        "commits_preprocessed.csv"
    ),
    index=False
)

files_p.to_csv(
    os.path.join(
        PREPROCESSED_DIR,
        "files_preprocessed.csv"
    ),
    index=False
)

# ============================================================
# FINAL CHECK
# ============================================================

print("\n==============================")
print("PREPROCESSING COMPLETED")
print("==============================")

print("Issues        :", len(issues_p))
print("Pull Requests :", len(pull_requests_p))
print("Commits       :", len(commits_p))
print("Files         :", len(files_p))

print("\nSaved to:")
print(PREPROCESSED_DIR)

print("==============================")