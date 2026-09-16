import pandas as pd
import os

# ==============================
# 1. Load dataset
# ==============================

input_path = "data/files.csv"
output_dir = "data/processed"
output_path = os.path.join(output_dir, "files_clean.csv")

os.makedirs(output_dir, exist_ok=True)

df = pd.read_csv(input_path)

print("================================")
print("FILES DATASET - PREPROCESSING")
print("================================")

print("\nOriginal shape:", df.shape)

# ==============================
# 2. Missing values
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
# 4. Validate commit SHA
# ==============================

print("\nMissing commit SHA:", df["commit_sha"].isnull().sum())

df = df.dropna(subset=["commit_sha"])

df["commit_sha"] = (
    df["commit_sha"]
    .astype(str)
    .str.strip()
)

df = df[df["commit_sha"] != ""]

# ==============================
# 5. Validate file names
# ==============================

print("Missing file names:", df["file_name"].isnull().sum())

df = df.dropna(subset=["file_name"])

df["file_name"] = (
    df["file_name"]
    .astype(str)
    .str.strip()
)

df = df[df["file_name"] != ""]

# ==============================
# 6. Clean file status
# ==============================

df["status"] = df["status"].fillna("unknown")

df["status"] = (
    df["status"]
    .astype(str)
    .str.strip()
    .str.lower()
)

print("\nFile statuses:")
print(df["status"].value_counts())

# ==============================
# 7. Validate PR number
# ==============================

df["pr_number"] = pd.to_numeric(
    df["pr_number"],
    errors="coerce"
)

print(
    "\nInvalid PR numbers:",
    df["pr_number"].isnull().sum()
)

df = df.dropna(subset=["pr_number"])

df["pr_number"] = df["pr_number"].astype(int)

# ==============================
# 8. Convert change statistics
# ==============================

numeric_columns = [
    "additions",
    "deletions",
    "changes"
]

for column in numeric_columns:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )

# Missing numerical values → 0
for column in numeric_columns:
    df[column] = df[column].fillna(0)

# ==============================
# 9. Validate negative values
# ==============================

print("\nNegative additions:", (df["additions"] < 0).sum())
print("Negative deletions:", (df["deletions"] < 0).sum())
print("Negative changes:", (df["changes"] < 0).sum())

# Remove impossible negative values
df = df[
    (df["additions"] >= 0) &
    (df["deletions"] >= 0) &
    (df["changes"] >= 0)
]

# ==============================
# 10. Check changes consistency
# ==============================

calculated_changes = (
    df["additions"] + df["deletions"]
)

inconsistent_changes = (
    df["changes"] != calculated_changes
).sum()

print(
    "\nInconsistent change counts:",
    inconsistent_changes
)

# ==============================
# 11. Final missing-value check
# ==============================

print("\nMissing values AFTER preprocessing:")
print(df.isnull().sum())

# ==============================
# 12. Final duplicate check
# ==============================

print("\nDuplicate rows AFTER preprocessing:")
print(df.duplicated().sum())

# ==============================
# 13. Save cleaned dataset
# ==============================

df.to_csv(output_path, index=False)

print("\n================================")
print("PREPROCESSING COMPLETED")
print("================================")

print("Final shape:", df.shape)

print("Saved to:", output_path)

print("\nFinal columns:")
print(list(df.columns))