import pandas as pd
from pathlib import Path

# ============================================
# REPORESCUE - INSPECT BOTTLENECK LABELS
# ============================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "features"
    / "pr_bottleneck_labels.csv"
)

df = pd.read_csv(INPUT_FILE)

print("=" * 55)
print("BOTTLENECK LABEL INSPECTION")
print("=" * 55)

print(f"Total PRs: {len(df)}")

# ============================================
# 1. LABEL COUNTS
# ============================================

print("\n--- LABEL COUNTS ---")

print(
    df["bottleneck_label"]
    .value_counts(dropna=False)
)

# ============================================
# 2. LABEL PERCENTAGES
# ============================================

print("\n--- LABEL PERCENTAGES ---")

counts = df["bottleneck_label"].value_counts(
    dropna=False
)

print(
    (counts / len(df) * 100).round(2)
)

# ============================================
# 3. RESOLUTION TIME BY LABEL
# ============================================

print("\n--- RESOLUTION TIME BY LABEL ---")

print(
    df.groupby("bottleneck_label", dropna=False)[
        "observed_resolution_days"
    ].agg(
        ["count", "mean", "median", "min", "max"]
    )
)

# ============================================
# 4. BOTTLENECK PRs
# ============================================

print("\n--- BOTTLENECK PR RESOLUTION TIMES ---")

bottleneck_prs = df[
    df["bottleneck_label"] == 1
]

print(
    bottleneck_prs[
        "observed_resolution_days"
    ].describe()
)

# ============================================
# 5. NON-BOTTLENECK PRs
# ============================================

print("\n--- NON-BOTTLENECK PR RESOLUTION TIMES ---")

normal_prs = df[
    df["bottleneck_label"] == 0
]

print(
    normal_prs[
        "observed_resolution_days"
    ].describe()
)

# ============================================
# 6. CENSORED PRs
# ============================================

print("\n--- CENSORED PRs ---")

censored = df[
    df["bottleneck_label"].isna()
]

print(f"Censored PRs: {len(censored)}")

if len(censored) > 0:
    print(
        censored[
            "observation_age_days"
        ].describe()
    )

# ============================================
# 7. CHECK LABEL LOGIC
# ============================================

print("\n--- LABEL LOGIC CHECK ---")

invalid_zero = df[
    (df["bottleneck_label"] == 0)
    & (
        df["observed_resolution_days"]
        > 7
    )
]

invalid_one = df[
    (df["bottleneck_label"] == 1)
    & df["closed_at"].notna()
    & (
        df["observed_resolution_days"]
        <= 7
    )
]

print(
    f"Invalid label 0 cases: "
    f"{len(invalid_zero)}"
)

print(
    f"Invalid label 1 cases: "
    f"{len(invalid_one)}"
)

# ============================================
# 8. CHECK FOR NEGATIVE VALUES
# ============================================

negative_resolution = df[
    df["observed_resolution_days"]
    < 0
]

negative_age = df[
    df["observation_age_days"]
    < 0
]

print("\n--- NEGATIVE VALUE CHECK ---")

print(
    f"Negative resolution times: "
    f"{len(negative_resolution)}"
)

print(
    f"Negative observation ages: "
    f"{len(negative_age)}"
)

# ============================================
# 9. FINAL STATUS
# ============================================

print("\n" + "=" * 55)

if (
    len(invalid_zero) == 0
    and len(invalid_one) == 0
    and len(negative_resolution) == 0
    and len(negative_age) == 0
):
    print("LABEL VALIDATION: PASSED ✅")
else:
    print("LABEL VALIDATION: CHECK REQUIRED ⚠️")

print("=" * 55)