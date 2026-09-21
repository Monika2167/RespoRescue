import pandas as pd
from pathlib import Path


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

COMMITS_FILE = BASE_DIR / "data" / "cleaned" / "commits_clean.csv"
FILES_FILE = BASE_DIR / "data" / "cleaned" / "files_clean.csv"
PRS_FILE = BASE_DIR / "data" / "cleaned" / "pull_requests_clean.csv"
ISSUES_FILE = BASE_DIR / "data" / "cleaned" / "issues_clean.csv"

OUTPUT_DIR = BASE_DIR / "data" / "graph"
OUTPUT_FILE = OUTPUT_DIR / "temporal_features.csv"


# ---------------------------------------------------------
# Load datasets
# ---------------------------------------------------------
commits = pd.read_csv(COMMITS_FILE)
files = pd.read_csv(FILES_FILE)
prs = pd.read_csv(PRS_FILE)
issues = pd.read_csv(ISSUES_FILE)

print("Datasets loaded successfully.")
print(f"Commits: {len(commits)}")
print(f"File changes: {len(files)}")
print(f"Pull requests: {len(prs)}")
print(f"Issues: {len(issues)}")


# ---------------------------------------------------------
# Convert timestamps to UTC
# ---------------------------------------------------------
commits["commit_date"] = pd.to_datetime(
    commits["commit_date"],
    utc=True,
    errors="coerce"
)

prs["created_at"] = pd.to_datetime(
    prs["created_at"],
    utc=True,
    errors="coerce"
)

prs["updated_at"] = pd.to_datetime(
    prs["updated_at"],
    utc=True,
    errors="coerce"
)

prs["closed_at"] = pd.to_datetime(
    prs["closed_at"],
    utc=True,
    errors="coerce"
)

prs["merged_at"] = pd.to_datetime(
    prs["merged_at"],
    utc=True,
    errors="coerce"
)

issues["created_at"] = pd.to_datetime(
    issues["created_at"],
    utc=True,
    errors="coerce"
)

issues["updated_at"] = pd.to_datetime(
    issues["updated_at"],
    utc=True,
    errors="coerce"
)

issues["closed_at"] = pd.to_datetime(
    issues["closed_at"],
    utc=True,
    errors="coerce"
)


# ---------------------------------------------------------
# Attach commit date to file changes
# ---------------------------------------------------------
files = files.merge(
    commits[["commit_sha", "commit_date"]],
    on="commit_sha",
    how="left"
)


# ---------------------------------------------------------
# Helper function
# ---------------------------------------------------------
def make_week(timestamp_series):
    return (
        timestamp_series
        .dt.tz_localize(None)
        .dt.to_period("W")
        .dt.start_time
    )


# ---------------------------------------------------------
# Create weekly periods
# ---------------------------------------------------------
commits["week"] = make_week(
    commits["commit_date"]
)

files["week"] = make_week(
    files["commit_date"]
)

prs["created_week"] = make_week(
    prs["created_at"]
)

prs["updated_week"] = make_week(
    prs["updated_at"]
)

prs["closed_week"] = make_week(
    prs["closed_at"]
)

prs["merged_week"] = make_week(
    prs["merged_at"]
)

issues["created_week"] = make_week(
    issues["created_at"]
)

issues["updated_week"] = make_week(
    issues["updated_at"]
)

issues["closed_week"] = make_week(
    issues["closed_at"]
)


# ---------------------------------------------------------
# Determine complete weekly range
# ---------------------------------------------------------
all_weeks = pd.concat(
    [
        commits["week"].dropna(),
        files["week"].dropna(),
        prs["created_week"].dropna(),
        prs["updated_week"].dropna(),
        prs["closed_week"].dropna(),
        prs["merged_week"].dropna(),
        issues["created_week"].dropna(),
        issues["updated_week"].dropna(),
        issues["closed_week"].dropna()
    ],
    ignore_index=True
)

week_range = pd.date_range(
    start=all_weeks.min(),
    end=all_weeks.max(),
    freq="7D"
)

weekly = pd.DataFrame(
    {"week": week_range}
)


# ---------------------------------------------------------
# 1. Commit activity
# ---------------------------------------------------------
commit_metrics = (
    commits
    .dropna(subset=["week"])
    .groupby("week")
    .agg(
        commits_per_week=("commit_sha", "nunique"),
        active_developers=("author", "nunique")
    )
    .reset_index()
)


# ---------------------------------------------------------
# 2. File activity and change volume
# ---------------------------------------------------------
files["changes"] = pd.to_numeric(
    files["changes"],
    errors="coerce"
).fillna(0)

files["additions"] = pd.to_numeric(
    files["additions"],
    errors="coerce"
).fillna(0)

files["deletions"] = pd.to_numeric(
    files["deletions"],
    errors="coerce"
).fillna(0)


file_metrics = (
    files
    .dropna(subset=["week"])
    .groupby("week")
    .agg(
        files_changed_per_week=("file_name", "count"),
        additions_per_week=("additions", "sum"),
        deletions_per_week=("deletions", "sum"),
        change_volume_per_week=("changes", "sum")
    )
    .reset_index()
)


# ---------------------------------------------------------
# 3. PR creation activity
# ---------------------------------------------------------
pr_created_metrics = (
    prs
    .dropna(subset=["created_week"])
    .groupby("created_week")
    .agg(
        prs_per_week=("pr_number", "count"),
        pr_authors=("author", "nunique"),
        pr_created_per_week=("pr_number", "count")
    )
    .reset_index()
    .rename(
        columns={"created_week": "week"}
    )
)


# ---------------------------------------------------------
# 4. PR update activity
# ---------------------------------------------------------
pr_updated_metrics = (
    prs
    .dropna(subset=["updated_week"])
    .groupby("updated_week")
    .agg(
        pr_updated_per_week=("pr_number", "count")
    )
    .reset_index()
    .rename(
        columns={"updated_week": "week"}
    )
)


# ---------------------------------------------------------
# 5. PR closure activity
# ---------------------------------------------------------
pr_closed_metrics = (
    prs
    .dropna(subset=["closed_week"])
    .groupby("closed_week")
    .agg(
        pr_closed_per_week=("pr_number", "count")
    )
    .reset_index()
    .rename(
        columns={"closed_week": "week"}
    )
)


# ---------------------------------------------------------
# 6. PR merge activity
# ---------------------------------------------------------
pr_merged_metrics = (
    prs
    .dropna(subset=["merged_week"])
    .groupby("merged_week")
    .agg(
        pr_merged_per_week=("pr_number", "count")
    )
    .reset_index()
    .rename(
        columns={"merged_week": "week"}
    )
)


# ---------------------------------------------------------
# 7. Issue creation / update / closure activity
# ---------------------------------------------------------
issue_created_metrics = (
    issues
    .dropna(subset=["created_week"])
    .groupby("created_week")
    .agg(
        issues_created_per_week=("issue_number", "nunique")
    )
    .reset_index()
    .rename(
        columns={"created_week": "week"}
    )
)


issue_updated_metrics = (
    issues
    .dropna(subset=["updated_week"])
    .groupby("updated_week")
    .agg(
        issues_updated_per_week=("issue_number", "nunique")
    )
    .reset_index()
    .rename(
        columns={"updated_week": "week"}
    )
)


issue_closed_metrics = (
    issues
    .dropna(subset=["closed_week"])
    .groupby("closed_week")
    .agg(
        issues_closed_per_week=("issue_number", "nunique")
    )
    .reset_index()
    .rename(
        columns={"closed_week": "week"}
    )
)


# ---------------------------------------------------------
# 8. Developer-file relationship activity
#
# A relationship is identified by:
# developer + file
# ---------------------------------------------------------
dev_file_data = (
    files[
        [
            "week",
            "file_name",
            "commit_sha"
        ]
    ]
    .merge(
        commits[
            [
                "commit_sha",
                "author"
            ]
        ],
        on="commit_sha",
        how="inner"
    )
)

dev_file_data = dev_file_data.dropna(
    subset=[
        "week",
        "author",
        "file_name"
    ]
)

dev_file_data = dev_file_data.drop_duplicates(
    subset=[
        "week",
        "author",
        "file_name"
    ]
)


dev_file_metrics = (
    dev_file_data
    .groupby("week")
    .agg(
        active_developer_file_relationships=(
            "file_name",
            "count"
        ),
        active_developers_in_files=(
            "author",
            "nunique"
        )
    )
    .reset_index()
)


# ---------------------------------------------------------
# 9. New developer-file relationships
#
# First observed week of each developer-file relationship.
# ---------------------------------------------------------
first_relationship_week = (
    dev_file_data
    .groupby(
        [
            "author",
            "file_name"
        ]
    )["week"]
    .min()
    .reset_index()
)

first_relationship_week = (
    first_relationship_week
    .groupby("week")
    .size()
    .reset_index(
        name="new_developer_file_relationships"
    )
)


# ---------------------------------------------------------
# 10. Merge weekly metrics
# ---------------------------------------------------------
weekly = weekly.merge(
    commit_metrics,
    on="week",
    how="left"
)

weekly = weekly.merge(
    file_metrics,
    on="week",
    how="left"
)

weekly = weekly.merge(
    pr_created_metrics,
    on="week",
    how="left"
)

weekly = weekly.merge(
    pr_updated_metrics,
    on="week",
    how="left"
)

weekly = weekly.merge(
    pr_closed_metrics,
    on="week",
    how="left"
)

weekly = weekly.merge(
    pr_merged_metrics,
    on="week",
    how="left"
)

weekly = weekly.merge(
    issue_created_metrics,
    on="week",
    how="left"
)

weekly = weekly.merge(
    issue_updated_metrics,
    on="week",
    how="left"
)

weekly = weekly.merge(
    issue_closed_metrics,
    on="week",
    how="left"
)

weekly = weekly.merge(
    dev_file_metrics,
    on="week",
    how="left"
)

weekly = weekly.merge(
    first_relationship_week,
    on="week",
    how="left"
)


# ---------------------------------------------------------
# Fill missing activity with zero
# ---------------------------------------------------------
numeric_columns = [
    "commits_per_week",
    "active_developers",
    "prs_per_week",
    "pr_authors",
    "files_changed_per_week",
    "pr_created_per_week",
    "pr_updated_per_week",
    "pr_closed_per_week",
    "pr_merged_per_week",
    "issues_created_per_week",
    "issues_updated_per_week",
    "issues_closed_per_week",
    "active_developer_file_relationships",
    "active_developers_in_files",
    "new_developer_file_relationships",
    "additions_per_week",
    "deletions_per_week",
    "change_volume_per_week"
]

for column in numeric_columns:

    weekly[column] = weekly[column].fillna(0)

    weekly[column] = weekly[column].astype(int)


# ---------------------------------------------------------
# 11. Unresolved PR trend
# ---------------------------------------------------------
prs_for_unresolved = prs.dropna(
    subset=["created_at"]
).copy()

unresolved_counts = []

for week_start in weekly["week"]:

    week_end = (
        week_start
        + pd.Timedelta(
            days=6,
            hours=23,
            minutes=59,
            seconds=59
        )
    )

    created_by_week = (
        prs_for_unresolved["created_at"]
        .dt.tz_localize(None)
        <= week_end
    )

    closed_by_week = (
        prs_for_unresolved["closed_at"].notna()
        & (
            prs_for_unresolved["closed_at"]
            .dt.tz_localize(None)
            <= week_end
        )
    )

    unresolved = (
        created_by_week & ~closed_by_week
    ).sum()

    unresolved_counts.append(
        int(unresolved)
    )


weekly["unresolved_prs"] = unresolved_counts


# ---------------------------------------------------------
# 12. Unresolved issue backlog
# ---------------------------------------------------------
issues_for_backlog = issues.dropna(
    subset=["created_at"]
).copy()

unresolved_issue_counts = []

for week_start in weekly["week"]:

    week_end = (
        week_start
        + pd.Timedelta(
            days=6,
            hours=23,
            minutes=59,
            seconds=59
        )
    )

    created_by_week = (
        issues_for_backlog["created_at"]
        .dt.tz_localize(None)
        <= week_end
    )

    closed_by_week = (
        issues_for_backlog["closed_at"].notna()
        & (
            issues_for_backlog["closed_at"]
            .dt.tz_localize(None)
            <= week_end
        )
    )

    unresolved = (
        created_by_week & ~closed_by_week
    ).sum()

    unresolved_issue_counts.append(
        int(unresolved)
    )


weekly["unresolved_issues"] = (
    unresolved_issue_counts
)


# ---------------------------------------------------------
# 13. Repository activity volume
#
# Combines commit, PR, issue and file activity.
# ---------------------------------------------------------
weekly["repository_activity_volume"] = (
    weekly["commits_per_week"]
    + weekly["prs_per_week"]
    + weekly["issues_created_per_week"]
    + weekly["files_changed_per_week"]
)


# ---------------------------------------------------------
# 14. Four-week rolling activity average
#
# Uses current and previous weeks only.
# Therefore no future leakage.
# ---------------------------------------------------------
weekly["activity_4week_average"] = (
    weekly["repository_activity_volume"]
    .rolling(
        window=4,
        min_periods=1
    )
    .mean()
    .round(2)
)


# ---------------------------------------------------------
# 15. Activity pattern signal
#
# HIGH:
# current activity >= 1.5 x rolling average
#
# MEDIUM:
# current activity >= 1.2 x rolling average
#
# LOW:
# otherwise
# ---------------------------------------------------------
def activity_signal(row):

    current = row["repository_activity_volume"]
    average = row["activity_4week_average"]

    if average == 0:
        return "LOW"

    ratio = current / average

    if ratio >= 1.5:
        return "HIGH"

    if ratio >= 1.2:
        return "MEDIUM"

    return "LOW"


weekly["activity_pattern_signal"] = (
    weekly.apply(
        activity_signal,
        axis=1
    )
)


# ---------------------------------------------------------
# 16. Activity change percentage
#
# Compared with previous week only.
# ---------------------------------------------------------
weekly["activity_change_pct"] = (
    weekly["repository_activity_volume"]
    .pct_change()
    .replace(
        [float("inf"), float("-inf")],
        0
    )
    .fillna(0)
    .mul(100)
    .round(2)
)


# ---------------------------------------------------------
# Format week
# ---------------------------------------------------------
weekly["week"] = weekly["week"].dt.strftime(
    "%Y-%m-%d"
)


# ---------------------------------------------------------
# Final column order
# ---------------------------------------------------------
weekly = weekly[
    [
        "week",

        "commits_per_week",
        "active_developers",

        "prs_per_week",
        "pr_authors",
        "pr_created_per_week",
        "pr_updated_per_week",
        "pr_closed_per_week",
        "pr_merged_per_week",
        "unresolved_prs",

        "issues_created_per_week",
        "issues_updated_per_week",
        "issues_closed_per_week",
        "unresolved_issues",

        "files_changed_per_week",
        "additions_per_week",
        "deletions_per_week",
        "change_volume_per_week",

        "active_developer_file_relationships",
        "active_developers_in_files",
        "new_developer_file_relationships",

        "repository_activity_volume",
        "activity_4week_average",
        "activity_change_pct",
        "activity_pattern_signal"
    ]
]


# ---------------------------------------------------------
# Validation
# ---------------------------------------------------------
print("\nValidation:")
print(
    f"Weeks analysed: {len(weekly)}"
)

print(
    f"Columns: {len(weekly.columns)}"
)

print(
    "Missing values:",
    int(
        weekly.isna().sum().sum()
    )
)

print(
    "Duplicate rows:",
    int(
        weekly.duplicated().sum()
    )
)

print("\nWeekly range:")

print(
    weekly["week"].min(),
    "to",
    weekly["week"].max()
)

print("\nActivity pattern signals:")

print(
    weekly[
        "activity_pattern_signal"
    ].value_counts()
    .to_string()
)

print("\nSample:")

print(
    weekly.head(10).to_string(
        index=False
    )
)


# ---------------------------------------------------------
# Save output
# ---------------------------------------------------------
OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

weekly.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nTemporal analysis completed!")

print(
    f"Weeks analysed: {len(weekly)}"
)

print("\nOutput file:")

print(OUTPUT_FILE)