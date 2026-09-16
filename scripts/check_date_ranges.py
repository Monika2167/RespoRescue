import pandas as pd
import os

files = {
    "Issues": "data/issues.csv",
    "Pull Requests": "data/pull_requests.csv",
    "Commits": "data/commits.csv"
}

print("\n==============================")
print("DATASET DATE RANGE CHECK")
print("==============================")

for name, path in files.items():

    print(f"\n{name}")
    print("------------------------------")

    if not os.path.exists(path):
        print("File not found:", path)
        continue

    df = pd.read_csv(path)

    # Find date columns
    date_columns = [
        col for col in df.columns
        if "date" in col.lower() or "created" in col.lower()
    ]

    for col in date_columns:

        dates = pd.to_datetime(
            df[col],
            errors="coerce"
        )

        print(f"{col}:")
        print("  Earliest:", dates.min())
        print("  Latest  :", dates.max())
        print("  Range   :", dates.max() - dates.min())

# Files dataset uses commit SHA, so it has no direct date column
print("\nFiles")
print("------------------------------")
print("files.csv has no date column.")
print("Its temporal coverage depends on commits.csv.")

print("\n==============================")
print("CHECK COMPLETE")
print("==============================")