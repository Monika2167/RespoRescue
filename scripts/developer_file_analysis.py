import pandas as pd
import os


FILES_FILE = "data/cleaned/files_clean.csv"
COMMITS_FILE = "data/cleaned/commits_clean.csv"

OUTPUT_FILE = "data/graph/developer_file_relationships.csv"


def load_data():

    files = pd.read_csv(
        FILES_FILE,
        dtype=str
    )

    commits = pd.read_csv(
        COMMITS_FILE,
        dtype=str
    )

    files = files.dropna(
        subset=[
            "commit_sha",
            "file_name"
        ]
    )

    commits = commits.dropna(
        subset=[
            "commit_sha",
            "pr_number",
            "author",
            "commit_date"
        ]
    )

    return files, commits


def build_developer_file_relationships(
    files,
    commits
):

    # Keep only required columns
    commit_data = commits[
        [
            "commit_sha",
            "pr_number",
            "author",
            "commit_date"
        ]
    ].copy()

    file_data = files[
        [
            "commit_sha",
            "file_name",
            "additions",
            "deletions",
            "changes"
        ]
    ].copy()

    # Convert numeric columns
    for column in [
        "additions",
        "deletions",
        "changes"
    ]:

        file_data[column] = pd.to_numeric(
            file_data[column],
            errors="coerce"
        ).fillna(0)

    # Merge commit information with file information
    merged = file_data.merge(
        commit_data,
        on="commit_sha",
        how="inner"
    )

    # Convert date
    merged["commit_date"] = pd.to_datetime(
        merged["commit_date"],
        errors="coerce"
    )

    merged = merged.dropna(
        subset=[
            "author",
            "file_name",
            "commit_date"
        ]
    )

    # Group by developer + file
    relationship = (
        merged
        .groupby(
            [
                "author",
                "file_name"
            ]
        )
        .agg(
            commit_count=(
                "commit_sha",
                "nunique"
            ),

            additions=(
                "additions",
                "sum"
            ),

            deletions=(
                "deletions",
                "sum"
            ),

            total_changes=(
                "changes",
                "sum"
            ),

            pr_count=(
                "pr_number",
                "nunique"
            ),

            first_activity=(
                "commit_date",
                "min"
            ),

            last_activity=(
                "commit_date",
                "max"
            )
        )
        .reset_index()
    )

    # Activity duration in days
    relationship["activity_duration_days"] = (
        relationship["last_activity"]
        - relationship["first_activity"]
    ).dt.days

    # Activity frequency
    relationship["activity_frequency"] = (
        relationship["commit_count"]
        /
        (
            relationship["activity_duration_days"]
            + 1
        )
    )

    # Relationship strength
    relationship["relationship_strength"] = (
        relationship["commit_count"]
        + relationship["pr_count"]
        + (
            relationship["total_changes"]
            / 100
        )
    )

    # Sort for readability
    relationship = relationship.sort_values(
        [
            "author",
            "commit_count"
        ],
        ascending=[
            True,
            False
        ]
    )

    return relationship


def validate_output(result):

    print("\nVALIDATION")
    print("-" * 40)

    print(
        "Rows:",
        len(result)
    )

    print(
        "Unique developers:",
        result["author"].nunique()
    )

    print(
        "Unique files:",
        result["file_name"].nunique()
    )

    print(
        "Missing values:",
        int(result.isna().sum().sum())
    )

    print(
        "Duplicate developer-file relationships:",
        int(
            result.duplicated(
                subset=[
                    "author",
                    "file_name"
                ]
            ).sum()
        )
    )

    print(
        "Minimum relationship strength:",
        round(
            result["relationship_strength"].min(),
            2
        )
    )

    print(
        "Maximum relationship strength:",
        round(
            result["relationship_strength"].max(),
            2
        )
    )


def main():

    print("=" * 60)
    print("DEVELOPER-FILE RELATIONSHIP ANALYSIS")
    print("=" * 60)

    files, commits = load_data()

    print(
        "\nFile rows:",
        len(files)
    )

    print(
        "Commit rows:",
        len(commits)
    )

    result = build_developer_file_relationships(
        files,
        commits
    )

    os.makedirs(
        "data/graph",
        exist_ok=True
    )

    result.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        "\nSaved:",
        OUTPUT_FILE
    )

    print(
        "Developer-file relationships:",
        len(result)
    )

    print("\nSample results:")

    print(
        result.head(10).to_string(
            index=False
        )
    )

    validate_output(result)


if __name__ == "__main__":
    main()