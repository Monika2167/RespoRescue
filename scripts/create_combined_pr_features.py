import pandas as pd
from pathlib import Path

# ==========================================
# PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

PR_FEATURES_PATH = (
    BASE_DIR
    / "data"
    / "features"
    / "pr_features.csv"
)

CODE_FEATURES_PATH = (
    BASE_DIR
    / "data"
    / "features"
    / "pr_code_change_features.csv"
)

OUTPUT_DIR = BASE_DIR / "data" / "features"
OUTPUT_PATH = OUTPUT_DIR / "combined_pr_features.csv"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ==========================================
# LOAD
# ==========================================

print("=" * 60)
print("CREATING COMBINED PR FEATURE DATASET")
print("=" * 60)

pr = pd.read_csv(PR_FEATURES_PATH)
code = pd.read_csv(CODE_FEATURES_PATH)

print("\nPR features rows   :", len(pr))
print("Code features rows :", len(code))


# ==========================================
# CHECK PR ID UNIQUENESS
# ==========================================

if pr["pr_number"].duplicated().any():
    raise ValueError("Duplicate PR numbers found in PR features.")

if code["pr_number"].duplicated().any():
    raise ValueError("Duplicate PR numbers found in code-change features.")


# ==========================================
# MERGE
# ==========================================

combined = pr.merge(
    code,
    on="pr_number",
    how="left",
    suffixes=("", "_code")
)


# ==========================================
# CODE FEATURES FOR PRs WITHOUT COMMITS
# ==========================================

code_columns = [
    col for col in code.columns
    if col != "pr_number"
]

for col in code_columns:
    combined[col] = pd.to_numeric(
        combined[col],
        errors="coerce"
    ).fillna(0)


# ==========================================
# CHECK RESULT
# ==========================================

print("\nCombined rows :", len(combined))
print("Combined columns :", len(combined.columns))

print("\nMissing values:")
print(combined.isnull().sum())


# ==========================================
# DUPLICATE CHECK
# ==========================================

print("\nDuplicate rows:", combined.duplicated().sum())
print("Unique PRs:", combined["pr_number"].nunique())


# ==========================================
# SAVE
# ==========================================

combined.to_csv(
    OUTPUT_PATH,
    index=False
)

print("\n" + "=" * 60)
print("COMBINED PR FEATURES CREATED")
print("=" * 60)

print("\nSaved to:")
print(OUTPUT_PATH)