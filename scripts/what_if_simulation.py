import os
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "data")
GRAPH_DIR = os.path.join(DATA_DIR, "graph")

FILES_PATH = os.path.join(DATA_DIR, "cleaned", "files_clean.csv")
COMMITS_PATH = os.path.join(DATA_DIR, "cleaned", "commits_clean.csv")
PRS_PATH = os.path.join(DATA_DIR, "cleaned", "pull_requests_clean.csv")
ISSUES_PATH = os.path.join(DATA_DIR, "cleaned", "issues_clean.csv")
ISSUE_PR_PATH = os.path.join(DATA_DIR, "issue_pr_relationships.csv")

OUTPUT_PATH = os.path.join(GRAPH_DIR, "what_if_simulation.csv")


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def risk_level(share):
    """Convert concentration share into a simple risk level."""

    if share >= 0.75:
        return "HIGH"

    if share >= 0.50:
        return "MEDIUM"

    return "LOW"


def safe_unique(values):
    """Return unique non-null string values."""

    return sorted(
        set(
            str(v)
            for v in values
            if pd.notna(v)
        )
    )


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    print("Loading datasets...")

    files = pd.read_csv(FILES_PATH)
    commits = pd.read_csv(COMMITS_PATH)
    prs = pd.read_csv(PRS_PATH)
    issues = pd.read_csv(ISSUES_PATH)
    issue_pr = pd.read_csv(ISSUE_PR_PATH)

    print("Files:", len(files))
    print("Commits:", len(commits))
    print("PRs:", len(prs))
    print("Issues:", len(issues))
    print("Issue-PR relationships:", len(issue_pr))

    return files, commits, prs, issues, issue_pr


# ============================================================
# PREPARE DATA
# ============================================================

def prepare_data(files, commits, prs, issues, issue_pr):

    print("\nPreparing relationships...")

    # --------------------------------------------------------
    # Numeric columns
    # --------------------------------------------------------

    for column in ["additions", "deletions", "changes"]:

        if column in files.columns:

            files[column] = pd.to_numeric(
                files[column],
                errors="coerce"
            ).fillna(0)

    # --------------------------------------------------------
    # Commit author information
    # --------------------------------------------------------

    commit_author = (
        commits[
            ["commit_sha", "author", "pr_number"]
        ]
        .drop_duplicates()
    )

    # --------------------------------------------------------
    # Developer -> File relationships
    # --------------------------------------------------------

    developer_files = files.merge(
        commit_author,
        on="commit_sha",
        how="inner"
    )

    developer_files = developer_files.dropna(
        subset=["author", "file_name"]
    )

    developer_files["author"] = (
        developer_files["author"]
        .astype(str)
    )

    developer_files["file_name"] = (
        developer_files["file_name"]
        .astype(str)
    )

    # --------------------------------------------------------
    # Developer-file commit counts
    # --------------------------------------------------------

    relationship_counts = (
        developer_files
        .groupby(
            ["author", "file_name"],
            as_index=False
        )
        .agg(
            commit_count=("commit_sha", "nunique"),
            total_changes=("changes", "sum"),
            pr_count=("pr_number_x", "nunique")
        )
    )

    # --------------------------------------------------------
    # File total commits
    # --------------------------------------------------------

    file_totals = (
        relationship_counts
        .groupby("file_name")["commit_count"]
        .sum()
        .to_dict()
    )

    # --------------------------------------------------------
    # File -> Developers
    # --------------------------------------------------------

    file_developers = {}

    for file_name, group in relationship_counts.groupby("file_name"):

        file_developers[str(file_name)] = {
            str(row.author): float(row.commit_count)
            for row in group.itertuples()
        }

    # --------------------------------------------------------
    # Developer -> Files
    # --------------------------------------------------------

    developer_files_map = {}

    for developer, group in relationship_counts.groupby("author"):

        developer_files_map[str(developer)] = group

    # --------------------------------------------------------
    # File -> PRs
    # --------------------------------------------------------

    file_pr_map = {}

    for file_name, group in files.groupby("file_name"):

        prs_for_file = safe_unique(
            group["pr_number"]
        )

        file_pr_map[str(file_name)] = prs_for_file

    # --------------------------------------------------------
    # Developer -> PRs
    # --------------------------------------------------------

    developer_pr_map = {}

    developer_commit_data = commits.dropna(
        subset=["author", "pr_number"]
    ).copy()

    for developer, group in developer_commit_data.groupby("author"):

        developer_pr_map[str(developer)] = safe_unique(
            group["pr_number"]
        )

    # --------------------------------------------------------
    # PR -> Issues
    # --------------------------------------------------------

    pr_issue_map = {}

    if (
        "pr_number" in issue_pr.columns
        and "issue_number" in issue_pr.columns
    ):

        for pr_number, group in issue_pr.groupby("pr_number"):

            pr_issue_map[str(pr_number)] = safe_unique(
                group["issue_number"]
            )

    # --------------------------------------------------------
    # PR dates
    # --------------------------------------------------------

    if "created_at" in prs.columns:

        prs["created_at"] = pd.to_datetime(
            prs["created_at"],
            errors="coerce"
        )

    print("Relationships prepared successfully.")

    return (
        relationship_counts,
        file_totals,
        file_developers,
        developer_files_map,
        file_pr_map,
        developer_pr_map,
        pr_issue_map,
        prs
    )


# ============================================================
# SCENARIO 1
# DEVELOPER UNAVAILABLE
# ============================================================

def simulate_developer_unavailable(
    relationship_counts,
    file_totals,
    file_developers,
    developer_files_map,
    file_pr_map,
    developer_pr_map,
    pr_issue_map
):

    print("\n----------------------------------------")
    print("SCENARIO 1: DEVELOPER UNAVAILABLE")
    print("----------------------------------------")

    rows = []

    developers = sorted(
        developer_files_map.keys()
    )

    print("Developers:", len(developers))

    for index, developer in enumerate(
        developers,
        start=1
    ):

        developer_data = developer_files_map[developer]

        for row in developer_data.itertuples():

            file_name = str(row.file_name)

            developer_commits = float(
                row.commit_count
            )

            total_commits = float(
                file_totals.get(file_name, 0)
            )

            if total_commits <= 0:
                continue

            # ---------------------------------------------
            # BEFORE
            # ---------------------------------------------

            before_share = (
                developer_commits /
                total_commits
            )

            before_risk = risk_level(
                before_share
            )

            # ---------------------------------------------
            # AFTER
            # Remove developer's contribution
            # ---------------------------------------------

            developers_for_file = (
                file_developers
                .get(file_name, {})
                .copy()
            )

            developers_for_file.pop(
                developer,
                None
            )

            remaining_total = sum(
                developers_for_file.values()
            )

            if remaining_total > 0:

                dominant_after = max(
                    developers_for_file.values()
                )

                after_share = (
                    dominant_after /
                    remaining_total
                )

            else:

                after_share = 0

            after_risk = risk_level(
                after_share
            )

            # ---------------------------------------------
            # AFFECTED ENTITIES
            # ---------------------------------------------

            affected_developers = safe_unique(
                developers_for_file.keys()
            )

            affected_prs = (
                developer_pr_map
                .get(developer, [])
            )

            file_prs = file_pr_map.get(
                file_name,
                []
            )

            affected_prs = sorted(
                set(
                    affected_prs +
                    file_prs
                )
            )

            affected_issues = []

            for pr in affected_prs:

                affected_issues.extend(
                    pr_issue_map.get(
                        str(pr),
                        []
                    )
                )

            affected_issues = sorted(
                set(affected_issues)
            )

            entities = [
                f"DEVELOPER:{developer}",
                f"FILE:{file_name}"
            ]

            entities.extend(
                f"DEVELOPER:{d}"
                for d in affected_developers[:20]
            )

            entities.extend(
                f"PR:{p}"
                for p in affected_prs[:20]
            )

            entities.extend(
                f"ISSUE:{i}"
                for i in affected_issues[:20]
            )

            # ---------------------------------------------
            # OUTPUT
            # ---------------------------------------------

            rows.append({

                "scenario_type":
                    "DEVELOPER_UNAVAILABLE",

                "scenario_status":
                    "SIMULATED",

                "target_developer":
                    developer,

                "target_file":
                    file_name,

                "target_pr":
                    "",

                "before_value":
                    round(before_share, 6),

                "after_value":
                    round(after_share, 6),

                "change":
                    round(
                        after_share -
                        before_share,
                        6
                    ),

                "before_concentration_risk":
                    before_risk,

                "after_concentration_risk":
                    after_risk,

                "risk_change":
                    (
                        "NO_CHANGE"
                        if before_risk == after_risk
                        else
                        f"{before_risk}_TO_{after_risk}"
                    ),

                "relationship_change":
                    "DEVELOPER_FILE_RELATIONSHIP_REMOVED",

                "affected_entity_count":
                    len(set(entities)),

                "affected_entity_types":
                    "DEVELOPER,FILE,PR,ISSUE",

                "affected_entities":
                    ";".join(
                        list(dict.fromkeys(entities))
                    ),

                "affected_developers":
                    ";".join(
                        affected_developers[:30]
                    ),

                "affected_files":
                    file_name,

                "affected_prs":
                    ";".join(
                        affected_prs[:30]
                    ),

                "affected_issues":
                    ";".join(
                        affected_issues[:30]
                    ),

                "impact_paths":
                    (
                        f"DEVELOPER:{developer}"
                        f" -> FILE:{file_name}"
                    ),

                "evidence":
                    (
                        "Simulated removal of the "
                        "developer-file relationship "
                        "using observed repository data."
                    )
            })

        if (
            index % 50 == 0
            or index == len(developers)
        ):

            print(
                f"Developers processed: "
                f"{index}/{len(developers)}"
            )

    return rows


# ============================================================
# SCENARIO 2
# FILE CHANGE
# ============================================================

def simulate_file_change(
    relationship_counts,
    file_developers,
    file_pr_map
):

    print("\n----------------------------------------")
    print("SCENARIO 2: FILE CHANGE")
    print("----------------------------------------")

    rows = []

    files = sorted(
        file_developers.keys()
    )

    print("Files:", len(files))

    for index, file_name in enumerate(
        files,
        start=1
    ):

        developers = file_developers[
            file_name
        ]

        total_commits = sum(
            developers.values()
        )

        developer_names = sorted(
            developers.keys()
        )

        affected_prs = file_pr_map.get(
            file_name,
            []
        )

        entities = [
            f"FILE:{file_name}"
        ]

        entities.extend(
            f"DEVELOPER:{d}"
            for d in developer_names[:30]
        )

        entities.extend(
            f"PR:{p}"
            for p in affected_prs[:30]
        )

        rows.append({

            "scenario_type":
                "FILE_CHANGE",

            "scenario_status":
                "SIMULATED",

            "target_developer":
                "",

            "target_file":
                file_name,

            "target_pr":
                "",

            "before_value":
                total_commits,

            "after_value":
                total_commits,

            "change":
                0,

            "before_concentration_risk":
                "OBSERVED",

            "after_concentration_risk":
                "REQUIRES_NEW_CHANGE_DATA",

            "risk_change":
                "NOT_ESTIMATED",

            "relationship_change":
                "FILE_SELECTED_FOR_CHANGE",

            "affected_entity_count":
                len(entities),

            "affected_entity_types":
                "FILE,DEVELOPER,PR",

            "affected_entities":
                ";".join(entities),

            "affected_developers":
                ";".join(
                    developer_names[:30]
                ),

            "affected_files":
                file_name,

            "affected_prs":
                ";".join(
                    affected_prs[:30]
                ),

            "affected_issues":
                "",

            "impact_paths":
                f"FILE:{file_name} -> DEVELOPER",

            "evidence":
                (
                    "Selected file for simulated "
                    "change using observed "
                    "developer-file relationships."
                )
        })

        if (
            index % 1000 == 0
            or index == len(files)
        ):

            print(
                f"Files processed: "
                f"{index}/{len(files)}"
            )

    return rows


# ============================================================
# SCENARIO 3
# PR DELAY
# ============================================================

def simulate_pr_delay(
    prs,
    file_pr_map,
    pr_issue_map,
    developer_pr_map
):

    print("\n----------------------------------------")
    print("SCENARIO 3: PR DELAY")
    print("----------------------------------------")

    rows = []

    valid_prs = prs[
        prs["pr_number"].notna()
    ].copy()

    print(
        "PRs available:",
        len(valid_prs)
    )

    for index, row in enumerate(
        valid_prs.itertuples(),
        start=1
    ):

        pr_number = str(
            row.pr_number
        )

        # ---------------------------------------------
        # Files affected by this PR
        # ---------------------------------------------

        affected_files = []

        for file_name, pr_list in file_pr_map.items():

            if pr_number in {
                str(x)
                for x in pr_list
            }:

                affected_files.append(
                    file_name
                )

        # ---------------------------------------------
        # Issues
        # ---------------------------------------------

        affected_issues = pr_issue_map.get(
            pr_number,
            []
        )

        # ---------------------------------------------
        # Developers
        # ---------------------------------------------

        affected_developers = []

        for developer, pr_list in developer_pr_map.items():

            if pr_number in {
                str(x)
                for x in pr_list
            }:

                affected_developers.append(
                    developer
                )

        entities = [
            f"PR:{pr_number}"
        ]

        entities.extend(
            f"FILE:{f}"
            for f in affected_files[:30]
        )

        entities.extend(
            f"DEVELOPER:{d}"
            for d in affected_developers[:30]
        )

        entities.extend(
            f"ISSUE:{i}"
            for i in affected_issues[:30]
        )

        rows.append({

            "scenario_type":
                "PR_DELAY",

            "scenario_status":
                "SIMULATED",

            "target_developer":
                "",

            "target_file":
                "",

            "target_pr":
                pr_number,

            "before_value":
                0,

            "after_value":
                1,

            "change":
                1,

            "before_concentration_risk":
                "OBSERVED",

            "after_concentration_risk":
                "DELAYED",

            "risk_change":
                "PR_DELAY_SIMULATED",

            "relationship_change":
                "PR_PROGRESS_DELAYED",

            "affected_entity_count":
                len(entities),

            "affected_entity_types":
                "PR,FILE,DEVELOPER,ISSUE",

            "affected_entities":
                ";".join(entities),

            "affected_developers":
                ";".join(
                    affected_developers[:30]
                ),

            "affected_files":
                ";".join(
                    affected_files[:30]
                ),

            "affected_prs":
                pr_number,

            "affected_issues":
                ";".join(
                    affected_issues[:30]
                ),

            "impact_paths":
                (
                    f"PR:{pr_number}"
                    " -> FILE/ISSUE/DEVELOPER"
                ),

            "evidence":
                (
                    "Simulated delay of the "
                    "selected pull request. "
                    "Affected entities are "
                    "derived from observed "
                    "repository relationships."
                )
        })

        if (
            index % 500 == 0
            or index == len(valid_prs)
        ):

            print(
                f"PRs processed: "
                f"{index}/{len(valid_prs)}"
            )

    return rows


# ============================================================
# SAVE RESULTS
# ============================================================

def save_results(rows):

    print("\nSaving results...")

    result = pd.DataFrame(rows)

    os.makedirs(
        GRAPH_DIR,
        exist_ok=True
    )

    result.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print(
        "\nWhat-if simulation completed."
    )

    print(
        "Total rows:",
        len(result)
    )

    print(
        "Output:",
        OUTPUT_PATH
    )

    print("\nScenario counts:")

    print(
        result["scenario_type"]
        .value_counts()
    )

    return result


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("REPORESCUE - WHAT-IF SIMULATION")
    print("=" * 60)

    try:

        (
            files,
            commits,
            prs,
            issues,
            issue_pr
        ) = load_data()

        (
            relationship_counts,
            file_totals,
            file_developers,
            developer_files_map,
            file_pr_map,
            developer_pr_map,
            pr_issue_map,
            prs
        ) = prepare_data(
            files,
            commits,
            prs,
            issues,
            issue_pr
        )

        # ----------------------------------------------------
        # Scenario 1
        # ----------------------------------------------------

        rows_1 = simulate_developer_unavailable(
            relationship_counts,
            file_totals,
            file_developers,
            developer_files_map,
            file_pr_map,
            developer_pr_map,
            pr_issue_map
        )

        # ----------------------------------------------------
        # Scenario 2
        # ----------------------------------------------------

        rows_2 = simulate_file_change(
            relationship_counts,
            file_developers,
            file_pr_map
        )

        # ----------------------------------------------------
        # Scenario 3
        # ----------------------------------------------------

        rows_3 = simulate_pr_delay(
            prs,
            file_pr_map,
            pr_issue_map,
            developer_pr_map
        )

        # ----------------------------------------------------
        # Combine
        # ----------------------------------------------------

        all_rows = (
            rows_1 +
            rows_2 +
            rows_3
        )

        save_results(
            all_rows
        )

    except Exception as error:

        print("\nERROR:")
        print(type(error).__name__)
        print(error)

        raise


if __name__ == "__main__":
    main()