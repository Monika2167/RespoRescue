import os
import pandas as pd


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATA_DIR = os.path.join(BASE_DIR, "data")
GRAPH_DIR = os.path.join(DATA_DIR, "graph")
CLEANED_DIR = os.path.join(DATA_DIR, "cleaned")

FILES_PATH = os.path.join(
    CLEANED_DIR, "files_clean.csv"
)

COMMITS_PATH = os.path.join(
    CLEANED_DIR, "commits_clean.csv"
)

PRS_PATH = os.path.join(
    CLEANED_DIR, "pull_requests_clean.csv"
)

ISSUE_PR_PATH = os.path.join(
    DATA_DIR, "issue_pr_relationships.csv"
)

TEMPORAL_PATH = os.path.join(
    GRAPH_DIR, "temporal_analysis.csv"
)

OUTPUT_PATH = os.path.join(
    GRAPH_DIR, "root_cause_candidates.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    print("Loading repository data...")

    files = pd.read_csv(FILES_PATH)
    commits = pd.read_csv(COMMITS_PATH)
    prs = pd.read_csv(PRS_PATH)
    issue_pr = pd.read_csv(ISSUE_PR_PATH)

    temporal = None

    if os.path.exists(TEMPORAL_PATH):

        temporal = pd.read_csv(
            TEMPORAL_PATH
        )

        print(
            "Temporal analysis loaded:",
            len(temporal)
        )

    else:

        print(
            "Temporal analysis not found."
        )

    print("Files:", len(files))
    print("Commits:", len(commits))
    print("PRs:", len(prs))
    print("Issue-PR relationships:", len(issue_pr))

    return (
        files,
        commits,
        prs,
        issue_pr,
        temporal
    )


# ============================================================
# BUILD CANDIDATE EVIDENCE
# ============================================================

def build_candidates(
    files,
    commits,
    prs,
    issue_pr,
    temporal
):

    print("\nBuilding root-cause candidate evidence...")

    # --------------------------------------------------------
    # Convert dates
    # --------------------------------------------------------

    commits["commit_date"] = pd.to_datetime(
        commits["commit_date"],
        errors="coerce"
    )

    prs["created_at"] = pd.to_datetime(
        prs["created_at"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # File change statistics
    # --------------------------------------------------------

    file_stats = (
        files
        .groupby("file_name")
        .agg(
            file_changes=("changes", "sum"),
            file_commit_count=("commit_sha", "nunique"),
            file_pr_count=("pr_number", "nunique")
        )
        .reset_index()
    )

    # --------------------------------------------------------
    # Commit statistics
    # --------------------------------------------------------

    commit_stats = (
        commits
        .groupby("commit_sha")
        .agg(
            commit_date=("commit_date", "min"),
            commit_author=("author", "first"),
            commit_pr=("pr_number", "first")
        )
        .reset_index()
    )

    # --------------------------------------------------------
    # Merge commit + file information
    # --------------------------------------------------------

    evidence = files.merge(
        commit_stats,
        on="commit_sha",
        how="left"
    )

    evidence = evidence.merge(
        file_stats,
        on="file_name",
        how="left"
    )

    # --------------------------------------------------------
    # PR information
    # --------------------------------------------------------

    pr_columns = [
        "pr_number",
        "title",
        "state",
        "created_at",
        "merged_at",
        "author"
    ]

    available_pr_columns = [
        c for c in pr_columns
        if c in prs.columns
    ]

    pr_data = prs[
        available_pr_columns
    ].copy()

    evidence = evidence.merge(
        pr_data,
        left_on="pr_number",
        right_on="pr_number",
        how="left",
        suffixes=("", "_pr")
    )

    # --------------------------------------------------------
    # Candidate evidence scores
    # --------------------------------------------------------

    evidence["recency_score"] = 0.0
    evidence["change_score"] = 0.0
    evidence["frequency_score"] = 0.0

    # Recent commits get stronger temporal evidence
    max_date = evidence["commit_date"].max()

    if pd.notna(max_date):

        days_old = (
            max_date -
            evidence["commit_date"]
        ).dt.days

        evidence["recency_score"] = (
            1 /
            (1 + days_old.clip(lower=0))
        )

    # Larger changes receive more evidence
    max_changes = evidence["changes"].max()

    if max_changes > 0:

        evidence["change_score"] = (
            evidence["changes"] /
            max_changes
        )

    # Files repeatedly changed receive more evidence
    max_frequency = (
        evidence["file_commit_count"]
        .max()
    )

    if max_frequency > 0:

        evidence["frequency_score"] = (
            evidence["file_commit_count"] /
            max_frequency
        )

    # --------------------------------------------------------
    # Combined candidate score
    # --------------------------------------------------------

    evidence["candidate_score"] = (

        evidence["recency_score"] * 0.40

        +

        evidence["change_score"] * 0.30

        +

        evidence["frequency_score"] * 0.30
    )

    # --------------------------------------------------------
    # Candidate type
    # --------------------------------------------------------

    evidence["candidate_type"] = (
        "COMMIT_FILE_CHANGE"
    )

    # --------------------------------------------------------
    # Evidence description
    # --------------------------------------------------------

    evidence["evidence"] = (
        "Candidate identified from "
        "temporal recency, file change "
        "magnitude, and repeated file activity."
    )

    # --------------------------------------------------------
    # Keep useful columns
    # --------------------------------------------------------

    output_columns = [
        "candidate_type",
        "candidate_score",
        "commit_sha",
        "commit_author",
        "commit_date",
        "pr_number",
        "title",
        "file_name",
        "changes",
        "additions",
        "deletions",
        "file_commit_count",
        "file_pr_count",
        "recency_score",
        "change_score",
        "frequency_score",
        "evidence"
    ]

    output_columns = [
        c for c in output_columns
        if c in evidence.columns
    ]

    result = evidence[
        output_columns
    ].copy()

    # --------------------------------------------------------
    # Sort candidates
    # --------------------------------------------------------

    result = result.sort_values(
        "candidate_score",
        ascending=False
    )

    # --------------------------------------------------------
    # Candidate rank
    # --------------------------------------------------------

    result.insert(
        0,
        "candidate_rank",
        range(1, len(result) + 1)
    )

    return result


# ============================================================
# SAVE RESULTS
# ============================================================

def save_results(result):

    os.makedirs(
        GRAPH_DIR,
        exist_ok=True
    )

    result.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print("\nRoot-cause candidate analysis completed.")

    print(
        "Total candidate evidence rows:",
        len(result)
    )

    print(
        "Output:",
        OUTPUT_PATH
    )

    print("\nTop 10 candidates:")

    print(
        result.head(10).to_string(
            index=False
        )
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("REPORESCUE - ROOT-CAUSE CANDIDATE DETECTION")
    print("=" * 60)

    (
        files,
        commits,
        prs,
        issue_pr,
        temporal
    ) = load_data()

    result = build_candidates(
        files,
        commits,
        prs,
        issue_pr,
        temporal
    )

    save_results(
        result
    )


if __name__ == "__main__":
    main()