import pandas as pd
from pathlib import Path

# ============================================
# REPORESCUE - CREATE BOTTLENECK LABELS
# ============================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "features"
    / "combined_pr_features.csv"
)

OUTPUT_DIR = BASE_DIR / "data" / "features"

OUTPUT_FILE = (
    OUTPUT_DIR
    / "pr_bottleneck_labels.csv"
)

# Bottleneck threshold
BOTTLENECK_DAYS = 7

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

print("=" * 50)
print("CREATING BOTTLENECK LABELS")
print("=" * 50)

# ============================================
# 1. LOAD DATA
# ============================================

df = pd.read_csv(INPUT_FILE)

print(f"Loaded PRs: {len(df)}")

# ============================================
# 2. CONVERT DATE COLUMNS
# ============================================

df["created_at"] = pd.to_datetime(
    df["created_at"],
    utc=True,
    errors="coerce"
)

df["closed_at"] = pd.to_datetime(
    df["closed_at"],
    utc=True,
    errors="coerce"
)

df["updated_at"] = pd.to_datetime(
    df["updated_at"],
    utc=True,
    errors="coerce"
)

# ============================================
# 3. DETERMINE OBSERVATION END
# ============================================
# We use the latest updated_at timestamp
# rather than the latest created_at timestamp.
#
# This represents the latest point in time
# for which our collected repository data
# contains observations.

observation_end = df["updated_at"].max()

print(f"Observation end: {observation_end}")

# ============================================
# 4. CALCULATE OBSERVED RESOLUTION TIME
# ============================================

df["observed_resolution_days"] = (
    df["closed_at"] - df["created_at"]
).dt.total_seconds() / (24 * 3600)

# ============================================
# 5. INITIALIZE LABEL
# ============================================
# 0 = Not a bottleneck
# 1 = Bottleneck
# NA = Censored / insufficient observation

df["bottleneck_label"] = pd.NA

# ============================================
# 6. CLOSED PRs
# ============================================

# Closed within 7 days
# → Not a bottleneck

closed_fast = (
    df["closed_at"].notna()
    & (
        df["observed_resolution_days"]
        <= BOTTLENECK_DAYS
    )
)

df.loc[
    closed_fast,
    "bottleneck_label"
] = 0


# Closed after 7 days
# → Bottleneck

closed_slow = (
    df["closed_at"].notna()
    & (
        df["observed_resolution_days"]
        > BOTTLENECK_DAYS
    )
)

df.loc[
    closed_slow,
    "bottleneck_label"
] = 1

# ============================================
# 7. CURRENTLY OPEN PRs
# ============================================

# Calculate how long each open PR has been
# observable in our dataset.

df["observation_age_days"] = (
    observation_end - df["created_at"]
).dt.total_seconds() / (24 * 3600)

# Open for more than 7 days
# → It has already crossed the bottleneck
# threshold.

open_old = (
    df["closed_at"].isna()
    & (
        df["observation_age_days"]
        > BOTTLENECK_DAYS
    )
)

df.loc[
    open_old,
    "bottleneck_label"
] = 1

# ============================================
# 8. RECENT OPEN PRs
# ============================================
# These PRs have not existed for more than
# 7 days, so we cannot know yet whether they
# will become bottlenecks.
#
# Therefore they remain NA.

recent_open = (
    df["closed_at"].isna()
    & (
        df["observation_age_days"]
        <= BOTTLENECK_DAYS
    )
)

df.loc[
    recent_open,
    "bottleneck_label"
] = pd.NA

# ============================================
# 9. SELECT FINAL LABEL DATA
# ============================================

label_columns = [
    "pr_number",
    "created_at",
    "updated_at",
    "closed_at",
    "observed_resolution_days",
    "observation_age_days",
    "bottleneck_label"
]

labels = df[label_columns].copy()

# ============================================
# 10. SUMMARY
# ============================================

print("\n" + "=" * 50)
print("BOTTLENECK LABEL SUMMARY")
print("=" * 50)

total_prs = len(labels)

not_bottleneck = (
    labels["bottleneck_label"] == 0
).sum()

bottleneck = (
    labels["bottleneck_label"] == 1
).sum()

censored = (
    labels["bottleneck_label"].isna()
).sum()

print(f"Total PRs                : {total_prs}")
print(
    f"Label 0 - Not bottleneck : "
    f"{not_bottleneck}"
)
print(
    f"Label 1 - Bottleneck     : "
    f"{bottleneck}"
)
print(
    f"Censored / Unknown      : "
    f"{censored}"
)

# ============================================
# 11. LABELED DATA PERCENTAGES
# ============================================

labeled_count = (
    not_bottleneck + bottleneck
)

if labeled_count > 0:

    label_0_percent = (
        not_bottleneck
        / labeled_count
        * 100
    )

    label_1_percent = (
        bottleneck
        / labeled_count
        * 100
    )

    print("\nLabeled PR distribution:")
    print(
        f"Not bottleneck : "
        f"{label_0_percent:.2f}%"
    )
    print(
        f"Bottleneck     : "
        f"{label_1_percent:.2f}%"
    )

# ============================================
# 12. LABEL VALUE COUNTS
# ============================================

print("\nLabel distribution:")

print(
    labels["bottleneck_label"]
    .value_counts(dropna=False)
)

# ============================================
# 13. SAVE
# ============================================

labels.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n" + "=" * 50)
print("BOTTLENECK LABEL CREATION COMPLETED")
print("=" * 50)

print("Saved to:")
print(OUTPUT_FILE)