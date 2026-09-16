import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_PATH = (
    BASE_DIR
    / "data"
    / "features"
    / "combined_pr_features.csv"
)

df = pd.read_csv(INPUT_PATH)

print("=" * 60)
print("BOTTLENECK TARGET ANALYSIS")
print("=" * 60)

# ==========================================
# CANDIDATE MAINTENANCE SIGNALS
# ==========================================

signals = [
    "resolution_time_days",
    "comments_count",
    "commits_count",
    "files_changed",
    "total_changes",
    "activity_score"
]

print("\n" + "=" * 60)
print("CANDIDATE SIGNAL STATISTICS")
print("=" * 60)

for col in signals:

    if col not in df.columns:
        print(f"{col}: NOT FOUND")
        continue

    print(f"\n{col}")

    print(
        df[col].describe(
            percentiles=[0.50, 0.75, 0.90, 0.95, 0.99]
        ).to_string()
    )


# ==========================================
# HIGH-TAIL COUNTS
# ==========================================

print("\n" + "=" * 60)
print("HIGH-TAIL COUNTS")
print("=" * 60)

for col in signals:

    if col not in df.columns:
        continue

    series = df[col].dropna()

    if len(series) == 0:
        continue

    q90 = series.quantile(0.90)
    q95 = series.quantile(0.95)

    print(
        f"\n{col}"
        f"\n  90th percentile : {q90:.3f}"
        f"\n  95th percentile : {q95:.3f}"
        f"\n  >= P90          : {(series >= q90).sum()}"
        f"\n  >= P95          : {(series >= q95).sum()}"
    )


# ==========================================
# CORRELATION BETWEEN CANDIDATE SIGNALS
# ==========================================

print("\n" + "=" * 60)
print("SIGNAL CORRELATION")
print("=" * 60)

available = [
    col for col in signals
    if col in df.columns
]

print(
    df[available]
    .corr()
    .round(3)
    .to_string()
)


# ==========================================
# EXISTING ACTIVITY DISTRIBUTION
# ==========================================

if "activity_score" in df.columns:

    print("\n" + "=" * 60)
    print("ACTIVITY SCORE DISTRIBUTION")
    print("=" * 60)

    print(
        df["activity_score"]
        .describe(
            percentiles=[
                0.50,
                0.75,
                0.80,
                0.90,
                0.95,
                0.99
            ]
        )
        .to_string()
    )


print("\n" + "=" * 60)
print("ANALYSIS COMPLETED")
print("=" * 60)