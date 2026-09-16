import pandas as pd
import os

# ==============================
# CONFIGURATION
# ==============================

DATA_DIR = "data"

FILES = {
    "issues": "data/issues.csv",
    "pull_requests": "data/pull_requests.csv",
    "commits": "data/commits.csv",
    "files": "data/files.csv"
}


# ==============================
# VALIDATION FUNCTION
# ==============================

def validate_dataset(name, path):

    print("\n" + "=" * 60)
    print(f"VALIDATING: {name.upper()}")
    print("=" * 60)

    if not os.path.exists(path):
        print(f"❌ File not found: {path}")
        return

    df = pd.read_csv(path, low_memory=False)

    print(f"Rows            : {len(df):,}")
    print(f"Columns         : {len(df.columns)}")
    print(f"Duplicate rows  : {df.duplicated().sum():,}")

    print("\nColumns:")
    print(list(df.columns))

    print("\nMissing values:")
    missing = df.isnull().sum()
    missing = missing[missing > 0]

    if len(missing) == 0:
        print("None ✅")
    else:
        print(missing)

    print("\nUnique values:")
    for column in df.columns:
        print(f"{column}: {df[column].nunique(dropna=True):,}")

    print("\nData types:")
    print(df.dtypes)

    return df


# ==============================
# VALIDATE ALL DATASETS
# ==============================

datasets = {}

for name, path in FILES.items():
    datasets[name] = validate_dataset(name, path)


# ==============================
# RELATIONSHIP VALIDATION
# ==============================

print("\n" + "=" * 60)
print("CROSS-DATASET VALIDATION")
print("=" * 60)

issues = datasets.get("issues")
prs = datasets.get("pull_requests")
commits = datasets.get("commits")
files = datasets.get("files")


# ------------------------------
# ISSUES
# ------------------------------

if issues is not None:

    if "issue_number" in issues.columns:
        print(
            f"\nIssues unique numbers: "
            f"{issues['issue_number'].nunique():,}"
        )

        print(
            f"Issues duplicated numbers: "
            f"{issues['issue_number'].duplicated().sum():,}"
        )


# ------------------------------
# PULL REQUESTS
# ------------------------------

if prs is not None:

    if "number" in prs.columns:

        print(
            f"\nPR unique numbers: "
            f"{prs['number'].nunique():,}"
        )

        print(
            f"PR duplicated numbers: "
            f"{prs['number'].duplicated().sum():,}"
        )

    elif "pr_number" in prs.columns:

        print(
            f"\nPR unique numbers: "
            f"{prs['pr_number'].nunique():,}"
        )


# ------------------------------
# COMMITS
# ------------------------------

if commits is not None:

    if "commit_sha" in commits.columns:

        print(
            f"\nUnique commits: "
            f"{commits['commit_sha'].nunique():,}"
        )

        print(
            f"Duplicate commit SHAs: "
            f"{commits['commit_sha'].duplicated().sum():,}"
        )

    if "pr_number" in commits.columns:

        print(
            f"Unique PRs in commits: "
            f"{commits['pr_number'].nunique():,}"
        )


# ------------------------------
# FILES
# ------------------------------

if files is not None:

    if "commit_sha" in files.columns:

        print(
            f"\nUnique commits represented in files: "
            f"{files['commit_sha'].nunique():,}"
        )

        print(
            f"Duplicate file rows: "
            f"{files.duplicated().sum():,}"
        )

    if "pr_number" in files.columns:

        print(
            f"Unique PRs represented in files: "
            f"{files['pr_number'].nunique():,}"
        )


# ==============================
# FINAL MESSAGE
# ==============================

print("\n" + "=" * 60)
print("VALIDATION COMPLETE")
print("=" * 60)