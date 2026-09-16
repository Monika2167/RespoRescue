import pandas as pd
from pathlib import Path

# ==========================================
# PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "preprocessed"


# ==========================================
# FUNCTION TO INSPECT DATASET
# ==========================================

def inspect_dataset(file_name):

    path = DATA_DIR / file_name
    df = pd.read_csv(path)

    print("\n" + "=" * 60)
    print(f"DATASET: {file_name}")
    print("=" * 60)

    # Shape
    print("\n--- Shape ---")
    print("Rows    :", df.shape[0])
    print("Columns :", df.shape[1])

    # Columns
    print("\n--- Columns ---")
    print(list(df.columns))

    # Datatypes
    print("\n--- Data Types ---")
    print(df.dtypes)

    # Missing values
    print("\n--- Missing Values ---")
    missing = df.isnull().sum()
    print(missing[missing > 0])

    if missing.sum() == 0:
        print("No missing values.")

    # Duplicate rows
    print("\n--- Duplicate Rows ---")
    print(df.duplicated().sum())

    # Numerical summary
    print("\n--- Numerical Summary ---")
    numeric_cols = df.select_dtypes(include="number").columns

    if len(numeric_cols) > 0:
        print(df[numeric_cols].describe())

    # Categorical / text information
    print("\n--- Categorical / Text Information ---")

    for col in df.select_dtypes(include="object").columns:

        print(f"\nColumn: {col}")
        print("Unique values:", df[col].nunique())

        if col in ["title", "body", "commit_message"]:
            lengths = df[col].fillna("").astype(str).str.len()

            print("Text length:")
            print("  Minimum :", lengths.min())
            print("  Maximum :", lengths.max())
            print("  Average :", round(lengths.mean(), 2))

    # Date information
    print("\n--- Date Information ---")

    date_keywords = ["date", "created_at", "updated_at", "closed_at", "merged_at"]

    for col in df.columns:

        if any(keyword in col.lower() for keyword in date_keywords):

            dates = pd.to_datetime(df[col], errors="coerce", utc=True)

            print(f"\n{col}")
            print("  Minimum:", dates.min())
            print("  Maximum:", dates.max())
            print("  Missing:", dates.isna().sum())


# ==========================================
# INSPECT ALL DATASETS
# ==========================================

files = [
    "issues_preprocessed.csv",
    "pull_requests_preprocessed.csv",
    "commits_preprocessed.csv",
    "files_preprocessed.csv"
]

for file in files:
    inspect_dataset(file)

print("\n" + "=" * 60)
print("PREPROCESSING INSPECTION COMPLETED")
print("=" * 60)