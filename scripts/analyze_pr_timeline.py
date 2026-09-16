import pandas as pd
from pathlib import Path

# ==========================================
# PATH
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_PATH = (
    BASE_DIR
    / "data"
    / "features"
    / "combined_pr_features.csv"
)

df = pd.read_csv(INPUT_PATH)

# ==========================================
# PREPARE DATES
# ==========================================

df["created_at"] = pd.to_datetime(
    df["created_at"],
    utc=True,
    errors="coerce"
)

df = df.sort_values("created_at").reset_index(drop=True)

# ==========================================
# BASIC TIMELINE
# ==========================================

print("=" * 60)
print("PR TEMPORAL ANALYSIS")
print("=" * 60)

print("\nTotal PRs:", len(df))

print("\nEarliest PR:")
print(df["created_at"].min())

print("\nLatest PR:")
print(df["created_at"].max())


# ==========================================
# QUANTILE-BASED TIME CUTS
# ==========================================

print("\n" + "=" * 60)
print("PROPOSED TEMPORAL SPLIT")
print("=" * 60)

train_end = df["created_at"].quantile(0.70)
validation_end = df["created_at"].quantile(0.85)

print("\n70% TRAIN cutoff:")
print(train_end)

print("\n85% VALIDATION cutoff:")
print(validation_end)

print("\nLatest 15% = TEST")


# ==========================================
# COUNT EACH SPLIT
# ==========================================

train = df[df["created_at"] <= train_end]

validation = df[
    (df["created_at"] > train_end)
    & (df["created_at"] <= validation_end)
]

test = df[df["created_at"] > validation_end]

print("\nSplit sizes:")

print("Train      :", len(train))
print("Validation :", len(validation))
print("Test       :", len(test))


# ==========================================
# DATE RANGES
# ==========================================

print("\n" + "=" * 60)
print("SPLIT DATE RANGES")
print("=" * 60)

for name, data in [
    ("TRAIN", train),
    ("VALIDATION", validation),
    ("TEST", test)
]:

    print(f"\n{name}")

    print("  Count :", len(data))
    print("  Start :", data["created_at"].min())
    print("  End   :", data["created_at"].max())


# ==========================================
# MONTHLY DISTRIBUTION
# ==========================================

print("\n" + "=" * 60)
print("MONTHLY PR DISTRIBUTION")
print("=" * 60)

monthly = (
    df.assign(
        month=df["created_at"].dt.to_period("M")
    )
    .groupby("month")
    .size()
)

print(monthly.to_string())


# ==========================================
# CHECK MISSING DATES
# ==========================================

print("\n" + "=" * 60)
print("DATE QUALITY")
print("=" * 60)

print(
    "Missing created_at:",
    df["created_at"].isna().sum()
)

print(
    "Duplicate PR numbers:",
    df["pr_number"].duplicated().sum()
)

print(
    "Chronologically sorted:",
    df["created_at"].is_monotonic_increasing
)


print("\n" + "=" * 60)
print("TIMELINE ANALYSIS COMPLETED")
print("=" * 60)