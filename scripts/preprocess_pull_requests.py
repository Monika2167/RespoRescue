import pandas as pd
import os

# ==============================
# 1. Load dataset
# ==============================

input_path = "data/pull_requests.csv"
output_dir = "data/processed"
output_path = os.path.join(output_dir, "pull_requests_clean.csv")

os.makedirs(output_dir, exist_ok=True)

df = pd.read_csv(input_path)

print("================================")
print("PULL REQUEST DATASET - PREPROCESSING")
print("================================")

print("\nOriginal shape:", df.shape)

# ==============================
# 2. Check missing values
# ==============================

print("\nMissing values BEFORE preprocessing:")
print(df.isnull().sum())

# ==============================
# 3. Remove exact duplicates
# ==============================

duplicates = df.duplicated().sum()

print("\nDuplicate rows:", duplicates)

if duplicates > 0:
    df = df.drop_duplicates()

# ==============================
# 4. Validate PR numbers
# ==============================

print("\nMissing PR numbers:", df["pr_number"].isnull().sum())
print("Duplicate PR numbers:", df["pr_number"].duplicated().sum())

df = df.dropna(subset=["pr_number"])

df["pr_number"] = df["pr_number"].astype(int)

# ==============================
# 5. Clean text columns
# ==============================

text_columns = [
    "title",
    "body",
    "state",
    "author",
    "html_url"
]

for column in text_columns:

    df[column] = df[column].fillna("")
    df[column] = df[column].astype(str)
    df[column] = df[column].str.strip()

# ==============================
# 6. Handle draft column
# ==============================

df["draft"] = df["draft"].fillna(False)

df["draft"] = df["draft"].astype(bool)

# ==============================
# 7. Convert date columns
# ==============================

date_columns = [
    "created_at",
    "updated_at",
    "closed_at",
    "merged_at"
]

for column in date_columns:

    df[column] = pd.to_datetime(
        df[column],
        errors="coerce",
        utc=True
    )

# IMPORTANT:
# closed_at can be missing for open PRs.
# merged_at can be missing for PRs that were not merged.
# We keep these missing values.

# ==============================
# 8. Validate PR state
# ==============================

print("\nPR states:")
print(df["state"].value_counts(dropna=False))

# ==============================
# 9. Final missing-value check
# ==============================

print("\nMissing values AFTER preprocessing:")
print(df.isnull().sum())

# ==============================
# 10. Final duplicate check
# ==============================

print("\nDuplicate rows AFTER preprocessing:")
print(df.duplicated().sum())

# ==============================
# 11. Save cleaned dataset
# ==============================

df.to_csv(output_path, index=False)

print("\n================================")
print("PREPROCESSING COMPLETED")
print("================================")

print("Final shape:", df.shape)
print("Saved to:", output_path)

print("\nFinal columns:")
print(list(df.columns))