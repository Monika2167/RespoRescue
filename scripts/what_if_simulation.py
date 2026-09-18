import pandas as pd
from pathlib import Path

# ============================================================
# Paths
# ============================================================
BASE_DIR = Path(__file__).resolve().parents[1]

COMMITS_FILE = BASE_DIR / "data" / "cleaned" / "commits_clean.csv"
FILES_FILE = BASE_DIR / "data" / "cleaned" / "files_clean.csv"

OUTPUT_DIR = BASE_DIR / "data" / "graph"

# Existing output - preserved
OUTPUT_FILE = OUTPUT_DIR / "what_if_results.csv"

# New scenario output
SCENARIO_OUTPUT_FILE = OUTPUT_DIR / "what_if_scenarios.csv"


# ============================================================
# Load data
# ============================================================
commits = pd.read_csv(
    COMMITS_FILE,
    usecols=["commit_sha", "author"]
)

files = pd.read_csv(
    FILES_FILE,
    usecols=["commit_sha", "pr_number", "file_name"]
)

print("Datasets loaded successfully.")
print("Commits:", len(commits))
print("File rows:", len(files))


# ============================================================
# Join developer -> file
# ============================================================
developer_files = files.merge(
    commits,
    on="commit_sha",
    how="inner"
)

developer_files = developer_files.dropna(
    subset=["author", "file_name"]
)

print(
    "Developer-file contribution rows:",
    len(developer_files)
)


# ============================================================
# Developer-file contribution count
# ============================================================
contribution = (
    developer_files
    .groupby(
        ["file_name", "author"],
        as_index=False
    )
    .size()
    .rename(columns={"size": "commit_count"})
)


# ============================================================
# File totals
# ============================================================
file_totals = (
    contribution
    .groupby("file_name")["commit_count"]
    .sum()
    .rename("total_commits")
)

contribution = contribution.merge(
    file_totals,
    on="file_name",
    how="left"
)


# ============================================================
# Developer share
# ============================================================
contribution["developer_share"] = (
    contribution["commit_count"]
    / contribution["total_commits"]
)


# ============================================================
# Dominant developer per file
# ============================================================
dominant = (
    contribution
    .sort_values(
        ["file_name", "developer_share", "author"],
        ascending=[True, False, True]
    )
    .drop_duplicates(
        "file_name",
        keep="first"
    )
)

dominant = dominant[
    [
        "file_name",
        "author",
        "developer_share",
        "total_commits"
    ]
].rename(
    columns={
        "author": "dominant_developer",
        "developer_share": "dominant_developer_share"
    }
)


# ============================================================
# Number of contributors
# ============================================================
contributors = (
    contribution
    .groupby("file_name")["author"]
    .nunique()
    .rename("unique_developers")
)

dominant = dominant.merge(
    contributors,
    on="file_name",
    how="left"
)


# ============================================================
# EXISTING WHAT-IF FEATURES
# ============================================================

dominant["files_losing_dominant_contributor"] = (
    dominant["dominant_developer_share"] >= 0.50
).astype(int)

dominant["files_with_no_remaining_contributor"] = (
    dominant["unique_developers"] == 1
).astype(int)

dominant["remaining_contributor_share"] = (
    1 - dominant["dominant_developer_share"]
)

dominant["high_concentration_flag"] = (
    dominant["dominant_developer_share"] >= 0.75
).astype(int)


# ============================================================
# SAVE EXISTING OUTPUT
# ============================================================
OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

dominant.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# NEW: DEVELOPER AVAILABILITY SCENARIO
# ============================================================
#
# Efficient approach:
# We calculate all remaining contribution values using
# grouped tables instead of filtering the full dataframe
# repeatedly.
# ============================================================

# Total contribution for each developer-file pair
# already available in `contribution`.

# For every file, calculate the total contribution excluding
# each developer.
contribution["remaining_commit_count"] = (
    contribution["total_commits"]
    - contribution["commit_count"]
)

contribution["remaining_share"] = (
    contribution["remaining_commit_count"]
    / contribution["total_commits"]
)

# Number of developers remaining after removing this developer
contribution["remaining_developers"] = (
    contribution["file_name"]
    .map(
        contribution
        .groupby("file_name")["author"]
        .nunique()
    )
    - 1
)

# Developer is dominant if their share equals maximum share
max_share = (
    contribution
    .groupby("file_name")["developer_share"]
    .transform("max")
)

contribution["is_dominant"] = (
    contribution["developer_share"] == max_share
).astype(int)


developer_scenarios = contribution.copy()

developer_scenarios["scenario_type"] = (
    "DEVELOPER_UNAVAILABLE"
)

developer_scenarios["target_developer"] = (
    developer_scenarios["author"]
)

developer_scenarios["target_file"] = (
    developer_scenarios["file_name"]
)

developer_scenarios["before_value"] = (
    developer_scenarios["developer_share"]
)

# After removing target developer, their own contribution = 0
developer_scenarios["after_value"] = 0.0

developer_scenarios["change"] = (
    developer_scenarios["after_value"]
    - developer_scenarios["before_value"]
)

developer_scenarios["remaining_contribution_records"] = (
    developer_scenarios["remaining_commit_count"]
)

developer_scenarios["affected"] = (
    developer_scenarios["is_dominant"]
)

# Scenario status
developer_scenarios["scenario_status"] = "NON_DOMINANT_CONTRIBUTOR_REMOVED"

developer_scenarios.loc[
    developer_scenarios["is_dominant"] == 1,
    "scenario_status"
] = "DOMINANT_CONTRIBUTOR_REMOVED"

developer_scenarios.loc[
    developer_scenarios["remaining_developers"] == 0,
    "scenario_status"
] = "NO_REMAINING_CONTRIBUTOR"

developer_scenarios["evidence"] = (
    developer_scenarios["target_developer"].astype(str)
    + " contributed "
    + developer_scenarios["commit_count"].astype(str)
    + " of "
    + developer_scenarios["total_commits"].astype(str)
    + " contribution records for this file."
)

developer_scenarios = developer_scenarios[
    [
        "scenario_type",
        "target_developer",
        "target_file",
        "before_value",
        "after_value",
        "change",
        "remaining_developers",
        "remaining_contribution_records",
        "affected",
        "scenario_status",
        "evidence"
    ]
]


# ============================================================
# NEW: FILE CHANGE SCENARIO
# ============================================================

file_developers = (
    contribution
    .groupby("file_name")
    .agg(
        related_developers=(
            "author",
            lambda x: "|".join(
                sorted(
                    x.astype(str).unique()
                )
            )
        ),
        developer_count=(
            "author",
            "nunique"
        ),
        total_contribution_records=(
            "commit_count",
            "sum"
        )
    )
    .reset_index()
)

file_scenarios = file_developers.copy()

file_scenarios["scenario_type"] = (
    "FILE_CHANGE"
)

file_scenarios["target_developer"] = ""

file_scenarios["target_file"] = (
    file_scenarios["file_name"]
)

# Current contribution record count
file_scenarios["before_value"] = (
    file_scenarios["total_contribution_records"]
)

# File-change scenario does not assume loss of contribution.
# Therefore before and after remain equal.
file_scenarios["after_value"] = (
    file_scenarios["total_contribution_records"]
)

file_scenarios["change"] = 0

file_scenarios["remaining_developers"] = (
    file_scenarios["developer_count"]
)

file_scenarios["remaining_contribution_records"] = (
    file_scenarios["total_contribution_records"]
)

file_scenarios["affected"] = 1

file_scenarios["scenario_status"] = (
    "DIRECT_FILE_ACTIVITY"
)

file_scenarios["evidence"] = (
    "File has "
    + file_scenarios["developer_count"].astype(str)
    + " developer(s) based on actual commit-file records."
)

file_scenarios = file_scenarios[
    [
        "scenario_type",
        "target_developer",
        "target_file",
        "before_value",
        "after_value",
        "change",
        "remaining_developers",
        "remaining_contribution_records",
        "affected",
        "scenario_status",
        "evidence"
    ]
]


# ============================================================
# Combine scenarios
# ============================================================
scenarios = pd.concat(
    [
        developer_scenarios,
        file_scenarios
    ],
    ignore_index=True
)


# ============================================================
# Validation / cleanup
# ============================================================
scenarios = scenarios.drop_duplicates()

scenarios = scenarios.reset_index(
    drop=True
)


# ============================================================
# Save new scenario output
# ============================================================
scenarios.to_csv(
    SCENARIO_OUTPUT_FILE,
    index=False
)


# ============================================================
# Final validation
# ============================================================
print("\n================================================")
print("WHAT-IF SIMULATION COMPLETED")
print("================================================")

print(
    "Files analyzed:",
    len(dominant)
)

print(
    "Files losing dominant contributor:",
    int(
        dominant[
            "files_losing_dominant_contributor"
        ].sum()
    )
)

print(
    "Files with no remaining contributor:",
    int(
        dominant[
            "files_with_no_remaining_contributor"
        ].sum()
    )
)

print(
    "Highly concentrated files:",
    int(
        dominant[
            "high_concentration_flag"
        ].sum()
    )
)

print("\nExisting output:")
print(OUTPUT_FILE)

print("\nNew scenario output:")
print(SCENARIO_OUTPUT_FILE)

print("\nScenario rows:", len(scenarios))

print("\nScenario types:")
print(
    scenarios[
        "scenario_type"
    ].value_counts()
)

print("\nExisting output shape:")
print(dominant.shape)

print(
    "Existing output missing values:",
    int(dominant.isna().sum().sum())
)

print(
    "Existing output duplicate rows:",
    int(dominant.duplicated().sum())
)

print("\nScenario output shape:")
print(scenarios.shape)

print(
    "Scenario output missing values:",
    int(scenarios.isna().sum().sum())
)

print(
    "Scenario output duplicate rows:",
    int(scenarios.duplicated().sum())
)

print("\nSample existing results:")
print(
    dominant.head(5).to_string(
        index=False
    )
)

print("\nSample scenario results:")
print(
    scenarios.head(5).to_string(
        index=False
    )
)