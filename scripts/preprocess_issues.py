import pandas as pd
import os

# ==============================
# 1. Load dataset
# ==============================

input_path = "data/issues.csv"
output_dir = "data/processed"
output_path = os.path.join(output_dir, "issues_clean.csv")

os.makedirs(output_dir, exist_ok=True)

df = pd.read_csv(input_path)

print("================================")
print("ISSUES DATASET - PREPROCESSING")
print("================================")

print("\nOriginal shape:", df.shape)

# ==============================
# 2. Check missing values
# ==============================

print("\nMissing values BEFORE preprocessing:")
print(df.isnull().sum())

# ==============================
# 3. Remove exact duplicate rows
# ==============================

duplicates = df.duplicated().sum()

print("\nDuplicate rows:", duplicates)

if duplicates > 0:
    df = df.drop_duplicates()

# ==============================
# 4. Validate issue numbers
# ==============================

print("\nMissing issue numbers:", df["issue_number"].isnull().sum())
print("Duplicate issue numbers:", df["issue_number"].duplicated().sum())

# Remove rows only if issue_number itself is missing
df = df.dropna(subset=["issue_number"])

# Make issue number integer
df["issue_number"] = df["issue_number"].astype(int)

# ==============================
# 5. Clean text columns
# ==============================

text_columns = ["title", "body", "author", "labels"]

for column in text_columns:

    # Missing text → empty string
    df[column] = df[column].fillna("")

    # Convert to string
    df[column] = df[column].astype(str)

    # Remove unnecessary spaces
    df[column] = df[column].str.strip()

# ==============================
# 6. Convert date columns
# ==============================

date_columns = [
    "created_at",
    "updated_at",
    "closed_at"
]

for column in date_columns:
    df[column] = pd.to_datetime(
        df[column],
        errors="coerce",
        utc=True
    )

# IMPORTANT:
# closed_at can legitimately be missing
# because an issue may still be OPEN.

# ==============================
# 7. Validate comments count
# ==============================

df["comments_count"] = pd.to_numeric(
    df["comments_count"],
    errors="coerce"
)

# Missing comments count → 0
df["comments_count"] = df["comments_count"].fillna(0)

# Comments cannot be negative
df = df[df["comments_count"] >= 0]

# ==============================
# 8. Final missing-value check
# ==============================

print("\nMissing values AFTER preprocessing:")
print(df.isnull().sum())

# ==============================
# 9. Final duplicate check
# ==============================

print("\nDuplicate rows AFTER preprocessing:")
print(df.duplicated().sum())

# ==============================
# 10. Save cleaned dataset
# ==============================

df.to_csv(output_path, index=False)

print("\n================================")
print("PREPROCESSING COMPLETED")
print("================================")

print("Final shape:", df.shape)
print("Saved to:", output_path)

print("\nFinal columns:")
print(list(df.columns))