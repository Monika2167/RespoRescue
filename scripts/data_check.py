import pandas as pd

files = [
    "issues.csv",
    "pull_requests.csv",
    "commits.csv",
    "files.csv"
]

for file in files:

    path = "data/" + file

    df = pd.read_csv(path)

    print("\n==============================")
    print(file)
    print("==============================")

    print("Rows:", len(df))
    print("Columns:", len(df.columns))

    print("\nColumn names:")
    print(list(df.columns))

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nDuplicate rows:", df.duplicated().sum())