import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

COMMITS_PATH = BASE_DIR / "data" / "cleaned" / "commits_clean.csv"
FILES_PATH = BASE_DIR / "data" / "cleaned" / "files_clean.csv"
OUTPUT_PATH = BASE_DIR / "data" / "graph" / "maintainer_bottlenecks.csv"


def main():
    print("=" * 70)
    print("MAINTAINER BOTTLENECK ANALYSIS")
    print("=" * 70)

    # --------------------------------------------------
    # LOAD REAL REPOSITORY DATA
    # --------------------------------------------------

    commits = pd.read_csv(COMMITS_PATH)
    files = pd.read_csv(FILES_PATH)

    print(f"\nCommits loaded : {len(commits)}")
    print(f"File rows loaded : {len(files)}")

    # --------------------------------------------------
    # KEEP ONLY REQUIRED REAL RELATIONSHIPS
    # --------------------------------------------------

    commits = commits[
        ["commit_sha", "pr_number", "author", "commit_date"]
    ].copy()

    files = files[
        ["commit_sha", "pr_number", "file_name", "changes"]
    ].copy()

    commits = commits.dropna(subset=["commit_sha", "author"])
    files = files.dropna(subset=["commit_sha", "file_name"])

    # --------------------------------------------------
    # JOIN DEVELOPER -> COMMIT -> FILE
    # --------------------------------------------------

    developer_files = files.merge(
        commits[["commit_sha", "author", "pr_number"]],
        on="commit_sha",
        how="inner",
        suffixes=("_file", "_commit")
    )

    developer_files["changes"] = pd.to_numeric(
        developer_files["changes"],
        errors="coerce"
    ).fillna(0)

    developer_files = developer_files.drop_duplicates(
        subset=["author", "commit_sha", "file_name"]
    )

    print(f"Developer-file contribution rows : {len(developer_files)}")

    # --------------------------------------------------
    # DEVELOPER LEVEL METRICS
    # --------------------------------------------------

    developer_summary = (
        developer_files
        .groupby("author")
        .agg(
            files_touched=("file_name", "nunique"),
            commits=("commit_sha", "nunique"),
            changes=("changes", "sum")
        )
        .reset_index()
        .rename(columns={"author": "developer"})
    )

    # --------------------------------------------------
    # REPOSITORY TOTALS
    # --------------------------------------------------

    total_files = developer_files["file_name"].nunique()
    total_commits = developer_files["commit_sha"].nunique()
    total_changes = developer_files["changes"].sum()

    # Avoid division by zero
    if total_files > 0:
        file_share = (
            developer_summary["files_touched"] / total_files
        )
    else:
        file_share = 0

    if total_commits > 0:
        commit_share = (
            developer_summary["commits"] / total_commits
        )
    else:
        commit_share = 0

    if total_changes > 0:
        change_share = (
            developer_summary["changes"] / total_changes
        )
    else:
        change_share = 0

    developer_summary["file_share"] = file_share
    developer_summary["commit_share"] = commit_share
    developer_summary["change_share"] = change_share

    # --------------------------------------------------
    # DEVELOPER CONCENTRATION
    # --------------------------------------------------
    # Transparent repository-level contribution signal.
    # It does NOT represent ownership.

    developer_summary["developer_concentration"] = (
        developer_summary["file_share"]
        + developer_summary["commit_share"]
        + developer_summary["change_share"]
    ) / 3

    # --------------------------------------------------
    # BOTTLENECK SCORE
    # --------------------------------------------------

    developer_summary["bottleneck_score"] = (
        developer_summary["developer_concentration"] * 100
    )

    # --------------------------------------------------
    # RISK LEVEL
    # --------------------------------------------------

    def classify_risk(score):
        if score >= 20:
            return "HIGH"
        elif score >= 10:
            return "MEDIUM"
        else:
            return "LOW"

    developer_summary["risk_level"] = (
        developer_summary["bottleneck_score"]
        .apply(classify_risk)
    )

    # --------------------------------------------------
    # EVIDENCE
    # --------------------------------------------------

    developer_summary["evidence"] = (
        "Observed contribution across "
        + developer_summary["files_touched"].astype(str)
        + " files, "
        + developer_summary["commits"].astype(str)
        + " commits, and "
        + developer_summary["changes"].round(0).astype(int).astype(str)
        + " changes."
    )

    # --------------------------------------------------
    # SORT BY BOTTLENECK SIGNAL
    # --------------------------------------------------

    developer_summary = developer_summary.sort_values(
        by="bottleneck_score",
        ascending=False
    ).reset_index(drop=True)

    # --------------------------------------------------
    # SAVE OUTPUT
    # --------------------------------------------------

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    developer_summary.to_csv(
        OUTPUT_PATH,
        index=False
    )

    # --------------------------------------------------
    # VALIDATION SUMMARY
    # --------------------------------------------------

    print("\n" + "=" * 70)
    print("BOTTLENECK SUMMARY")
    print("=" * 70)

    print(f"Developers analysed : {len(developer_summary)}")
    print(f"Unique files        : {total_files}")
    print(f"Unique commits      : {total_commits}")
    print(f"Total changes       : {total_changes:.0f}")

    print("\nRisk levels:")
    print(
        developer_summary["risk_level"]
        .value_counts()
        .to_string()
    )

    print("\nTop developers by bottleneck signal:")
    print(
        developer_summary[
            [
                "developer",
                "files_touched",
                "commits",
                "changes",
                "developer_concentration",
                "bottleneck_score",
                "risk_level"
            ]
        ]
        .head(10)
        .to_string(index=False)
    )

    print("\nOutput:")
    print(OUTPUT_PATH)

    print("\n" + "=" * 70)
    print("MAINTAINER BOTTLENECK ANALYSIS COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()