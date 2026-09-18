import pandas as pd
from pathlib import Path
from collections import defaultdict
from itertools import combinations

# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

FILES_FILE = BASE_DIR / "data" / "cleaned" / "files_clean.csv"
COMMITS_FILE = BASE_DIR / "data" / "cleaned" / "commits_clean.csv"
ISSUE_PR_FILE = BASE_DIR / "data" / "issue_pr_relationships.csv"

OUTPUT_DIR = BASE_DIR / "data" / "graph"

# Existing output - KEEPING THIS FEATURE
IMPACT_ANALYSIS_FILE = OUTPUT_DIR / "impact_analysis.csv"

# New API-friendly output
IMPACT_PROPAGATION_FILE = OUTPUT_DIR / "impact_propagation.csv"


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 60)
print("IMPACT PROPAGATION ANALYSIS")
print("=" * 60)

files = pd.read_csv(FILES_FILE)
commits = pd.read_csv(COMMITS_FILE)
issue_pr = pd.read_csv(ISSUE_PR_FILE)

print("\nDatasets loaded successfully.")
print("File rows    :", len(files))
print("Commit rows  :", len(commits))
print("Issue-PR rows:", len(issue_pr))


# ============================================================
# BASIC CLEANING
# ============================================================

files = files.dropna(
    subset=["commit_sha", "file_name"]
).copy()

commits = commits.dropna(
    subset=["pr_number", "commit_sha", "author"]
).copy()

issue_pr = issue_pr.dropna(
    subset=["issue_number", "pr_number"]
).copy()

# Keep IDs consistent
files["commit_sha"] = files["commit_sha"].astype(str)
files["file_name"] = files["file_name"].astype(str)

commits["commit_sha"] = commits["commit_sha"].astype(str)
commits["pr_number"] = commits["pr_number"].astype(str)
commits["author"] = commits["author"].astype(str)

issue_pr["issue_number"] = issue_pr["issue_number"].astype(str)
issue_pr["pr_number"] = issue_pr["pr_number"].astype(str)


# ============================================================
# PART 1
# EXISTING HISTORICAL CO-CHANGE ANALYSIS
#
# IMPORTANT:
# This section preserves the original feature.
# ============================================================

print("\n" + "-" * 60)
print("PART 1: HISTORICAL CO-CHANGE")
print("-" * 60)

commit_files = (
    files.groupby("commit_sha")["file_name"]
    .apply(lambda x: list(set(x)))
)

print("Commits with file information:", len(commit_files))

cochange_counts = defaultdict(int)

processed = 0

for commit_sha, file_list in commit_files.items():

    # Ignore commits containing only one file
    if len(file_list) < 2:
        continue

    # Safety limit for very large commits
    if len(file_list) > 100:
        continue

    for file_a, file_b in combinations(sorted(file_list), 2):
        cochange_counts[(file_a, file_b)] += 1

    processed += 1

    if processed % 1000 == 0:
        print("Processed commits:", processed)


records = []

for (source_file, target_file), frequency in cochange_counts.items():

    records.append({
        "source_file": source_file,
        "target_file": target_file,
        "cochange_frequency": frequency,
        "impact_weight": frequency
    })


impact_analysis = pd.DataFrame(records)

if not impact_analysis.empty:
    impact_analysis = impact_analysis.sort_values(
        "impact_weight",
        ascending=False
    )


OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Existing file remains unchanged in meaning
impact_analysis.to_csv(
    IMPACT_ANALYSIS_FILE,
    index=False
)

print("\nHistorical co-change relationships:",
      len(impact_analysis))

print("Saved:", IMPACT_ANALYSIS_FILE)


# ============================================================
# PART 2
# BUILD REAL PR → COMMIT → FILE RELATIONSHIPS
# ============================================================

print("\n" + "-" * 60)
print("PART 2: PR → COMMIT → FILE")
print("-" * 60)

commit_file_data = files[
    ["commit_sha", "file_name", "pr_number"]
].copy()

commit_file_data["pr_number"] = (
    commit_file_data["pr_number"]
    .astype(str)
)

commit_file_data = commit_file_data.drop_duplicates(
    ["pr_number", "commit_sha", "file_name"]
)

print(
    "Unique PR-commit-file relationships:",
    len(commit_file_data)
)


# ============================================================
# PART 3
# BUILD ISSUE → PR RELATIONSHIPS
# ============================================================

issue_pr_data = issue_pr[
    ["issue_number", "pr_number"]
].drop_duplicates()

print(
    "Unique Issue-PR relationships:",
    len(issue_pr_data)
)


# ============================================================
# PART 4
# BUILD IMPACT PROPAGATION OUTPUT
#
# Types:
# DIRECT
# RELATIONSHIP_BASED
# HISTORICAL
# ============================================================

print("\n" + "-" * 60)
print("PART 3: IMPACT PROPAGATION")
print("-" * 60)

propagation_records = []


# ------------------------------------------------------------
# DIRECT PR → COMMIT
# ------------------------------------------------------------

for row in commits[
    ["pr_number", "commit_sha", "author"]
].drop_duplicates().itertuples(index=False):

    pr_number = row.pr_number
    commit_sha = row.commit_sha
    author = row.author

    propagation_records.append({
        "impact_type": "DIRECT",
        "source_type": "PR",
        "source_id": pr_number,
        "related_type": "COMMIT",
        "related_id": commit_sha,
        "relationship": "PR_HAS_COMMIT",
        "evidence": "Commit belongs to the PR"
    })

    # --------------------------------------------------------
    # DIRECT COMMIT → DEVELOPER
    # --------------------------------------------------------

    propagation_records.append({
        "impact_type": "DIRECT",
        "source_type": "COMMIT",
        "source_id": commit_sha,
        "related_type": "DEVELOPER",
        "related_id": author,
        "relationship": "DEVELOPER_AUTHORED_COMMIT",
        "evidence": "Developer is recorded as commit author"
    })


# ------------------------------------------------------------
# DIRECT COMMIT → FILE
# ------------------------------------------------------------

for row in commit_file_data[
    ["commit_sha", "file_name"]
].drop_duplicates().itertuples(index=False):

    commit_sha = row.commit_sha
    file_name = row.file_name

    propagation_records.append({
        "impact_type": "DIRECT",
        "source_type": "COMMIT",
        "source_id": commit_sha,
        "related_type": "FILE",
        "related_id": file_name,
        "relationship": "COMMIT_MODIFIES_FILE",
        "evidence": "File is recorded in the commit file data"
    })


# ------------------------------------------------------------
# DIRECT PR → FILE
# ------------------------------------------------------------

pr_file_data = commit_file_data[
    ["pr_number", "file_name"]
].drop_duplicates()

for row in pr_file_data.itertuples(index=False):

    propagation_records.append({
        "impact_type": "DIRECT",
        "source_type": "PR",
        "source_id": row.pr_number,
        "related_type": "FILE",
        "related_id": row.file_name,
        "relationship": "PR_CHANGED_FILE",
        "evidence": "File was modified by a commit belonging to the PR"
    })


# ------------------------------------------------------------
# RELATIONSHIP-BASED PR → ISSUE
# ------------------------------------------------------------

for row in issue_pr_data.itertuples(index=False):

    propagation_records.append({
        "impact_type": "RELATIONSHIP_BASED",
        "source_type": "PR",
        "source_id": row.pr_number,
        "related_type": "ISSUE",
        "related_id": row.issue_number,
        "relationship": "ISSUE_HAS_PR",
        "evidence": "Explicit Issue-PR relationship in source data"
    })


# ------------------------------------------------------------
# RELATIONSHIP-BASED PR → DEVELOPER
# ------------------------------------------------------------

pr_developer_data = commits[
    ["pr_number", "author"]
].drop_duplicates()

for row in pr_developer_data.itertuples(index=False):

    propagation_records.append({
        "impact_type": "RELATIONSHIP_BASED",
        "source_type": "PR",
        "source_id": row.pr_number,
        "related_type": "DEVELOPER",
        "related_id": row.author,
        "relationship": "PR_COMMIT_AUTHOR",
        "evidence": "Developer authored a commit belonging to the PR"
    })


# ============================================================
# PART 5
# HISTORICAL FILE → FILE RELATIONSHIPS
#
# We use the existing co-change result.
# ============================================================

print("\nAdding historical file relationships...")

if not impact_analysis.empty:

    for row in impact_analysis.itertuples(index=False):

        propagation_records.append({
            "impact_type": "HISTORICAL",
            "source_type": "FILE",
            "source_id": row.source_file,
            "related_type": "FILE",
            "related_id": row.target_file,
            "relationship": "HISTORICAL_CO_CHANGE",
            "evidence": (
                "Files changed together in "
                + str(int(row.cochange_frequency))
                + " historical commits"
            )
        })


# ============================================================
# CREATE NEW PROPAGATION DATAFRAME
# ============================================================

impact_propagation = pd.DataFrame(
    propagation_records
)

# Remove exact duplicate relationships
impact_propagation = impact_propagation.drop_duplicates(
    subset=[
        "impact_type",
        "source_type",
        "source_id",
        "related_type",
        "related_id",
        "relationship"
    ]
)

# Sort for easier API/dashboard use
impact_propagation = impact_propagation.sort_values(
    by=[
        "impact_type",
        "source_type",
        "source_id",
        "related_type",
        "related_id"
    ]
)


# ============================================================
# SAVE NEW OUTPUT
# ============================================================

impact_propagation.to_csv(
    IMPACT_PROPAGATION_FILE,
    index=False
)

print("\nNew propagation relationships:",
      len(impact_propagation))

print("Saved:", IMPACT_PROPAGATION_FILE)


# ============================================================
# SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("IMPACT PROPAGATION SUMMARY")
print("=" * 60)

print("\nImpact types:")
print(
    impact_propagation["impact_type"]
    .value_counts()
    .to_string()
)

print("\nRelationship types:")
print(
    impact_propagation["relationship"]
    .value_counts()
    .to_string()
)

print("\nOutput columns:")
print(
    list(impact_propagation.columns)
)

print("\nSample:")
print(
    impact_propagation.head(15).to_string(index=False)
)

print("\n" + "=" * 60)
print("IMPACT PROPAGATION COMPLETED")
print("=" * 60)