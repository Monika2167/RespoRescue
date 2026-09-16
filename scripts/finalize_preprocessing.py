import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "preprocessed"


def process_file(file_name):
    path = DATA_DIR / file_name
    df = pd.read_csv(path)

    # -----------------------------
    # Text columns
    # -----------------------------
    text_columns = [
        col for col in ["title", "body", "commit_message"]
        if col in df.columns
    ]

    for col in text_columns:
        df[col] = df[col].fillna("").astype(str).str.strip()

    # -----------------------------
    # Labels
    # Keep missing labels meaningful
    # -----------------------------
    if "labels" in df.columns:
        df["labels"] = df["labels"].fillna("NO_LABEL")

    # -----------------------------
    # Dates
    # Convert to datetime
    # Keep missing dates as NaT
    # -----------------------------
    date_columns = [
        col for col in [
            "created_at",
            "updated_at",
            "closed_at",
            "merged_at",
            "commit_date"
        ]
        if col in df.columns
    ]

    for col in date_columns:
        df[col] = pd.to_datetime(
            df[col],
            errors="coerce",
            utc=True
        )

    # -----------------------------
    # Numeric columns
    # -----------------------------
    numeric_columns = [
        col for col in [
            "comments_count",
            "additions",
            "deletions",
            "changes"
        ]
        if col in df.columns
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        ).fillna(0)

        # No negative changes
        df[col] = df[col].clip(lower=0)

    # -----------------------------
    # Boolean
    # -----------------------------
    if "draft" in df.columns:
        df["draft"] = df["draft"].astype(bool)

    # -----------------------------
    # Save
    # -----------------------------
    df.to_csv(path, index=False)

    print(f"Processed: {file_name}")
    print(f"Rows: {len(df)}")


files = [
    "issues_preprocessed.csv",
    "pull_requests_preprocessed.csv",
    "commits_preprocessed.csv",
    "files_preprocessed.csv"
]

print("=" * 60)
print("FINALIZING PREPROCESSING")
print("=" * 60)

for file in files:
    process_file(file)

print("\n" + "=" * 60)
print("PREPROCESSING STEP 2 COMPLETED")
print("=" * 60)