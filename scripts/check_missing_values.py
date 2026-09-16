import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "preprocessed"


def check_file(file_name):
    path = DATA_DIR / file_name
    df = pd.read_csv(path)

    print("\n" + "=" * 60)
    print(file_name)
    print("=" * 60)

    for col in df.columns:

        null_count = df[col].isna().sum()

        if df[col].dtype == "string" or df[col].dtype == "object":
            empty_count = (df[col].fillna("") == "").sum()
        else:
            empty_count = 0

        print(
            f"{col:20} | "
            f"NaN: {null_count:5} | "
            f"Empty: {empty_count:5}"
        )


files = [
    "issues_preprocessed.csv",
    "pull_requests_preprocessed.csv",
    "commits_preprocessed.csv",
    "files_preprocessed.csv"
]

for file in files:
    check_file(file)

print("\n" + "=" * 60)
print("MISSING VALUE CHECK COMPLETED")
print("=" * 60)