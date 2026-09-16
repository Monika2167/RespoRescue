import pandas as pd
import os

# ==============================
# 1. Load dataset
# ==============================

input_path = "data/commits.csv"
output_dir = "data/processed"
output_path = os.path.join(output_dir, "commits_clean.csv")

os.makedirs(output_dir, exist_ok=True)

df = pd.read_csv(input_path)

print("================================")
print("COMMITS DATASET - PREPROCESSING")
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
# 4. Validate PR numbers
# ==============================

print("\nMissing PR numbers:", df["pr_number"].isnull().sum())

df = df.dropna(subset=["pr_number"])

df["pr_number"] = pd.to_numeric(
    df["pr_number"],
    errors="coerce"
)

df = df.dropna(subset=["pr_number"])

df["pr_number"] = df["pr_number"].astype(int)

# ==============================
# 5. Validate commit SHA
# ==============================

print("Missing commit SHA:", df["commit_sha"].isnull().sum())

df = df.dropna(subset=["commit_sha"])

df["commit_sha"] = df["commit_sha"].astype(str).str.strip()

# Remove empty SHA values
df = df[df["commit_sha"] != ""]

# ==============================
# 6. Clean commit messages
# ==============================

df["commit_message"] = df["commit_message"].fillna("")

df["commit_message"] = (
    df["commit_message"]
    .astype(str)
    .str.strip()
)

# ==============================
# 7. Clean author
# ==============================

df["author"] = df["author"].fillna("")

df["author"] = (
    df["author"]
    .astype(str)
    .str.strip()
)

# ==============================
# 8. Convert commit date
# ==============================

df["commit_date"] = pd.to_datetime(
    df["commit_date"],
    errors="coerce",
    utc=True
)

print(
    "\nInvalid commit dates:",
    df["commit_date"].isnull().sum()
)

# Remove rows where commit date is invalid
df = df.dropna(subset=["commit_date"])

# ==============================
# 9. Check duplicate commit SHA
# ==============================

print(
    "Duplicate commit SHA:",
    df["commit_sha"].duplicated().sum()
)

# A commit SHA should identify one commit.
df = df.drop_duplicates(
    subset=["commit_sha"]
)

# ==============================
# 10. Final missing-value check
# ==============================

print("\nMissing values AFTER preprocessing:")
print(df.isnull().sum())

# ==============================
# 11. Final duplicate check
# ==============================

print("\nDuplicate rows AFTER preprocessing:")
print(df.duplicated().sum())

# ==============================
# 12. Save cleaned dataset
# ==============================

df.to_csv(output_path, index=False)

print("\n================================")
print("PREPROCESSING COMPLETED")
print("================================")

print("Final shape:", df.shape)

print("Saved to:", output_path)

print("\nFinal columns:")
print(list(df.columns))