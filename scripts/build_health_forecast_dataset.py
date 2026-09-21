import pandas as pd


# ============================================================
# 1. Load cleaned source data
# ============================================================

issues = pd.read_csv("data/cleaned/issues_clean.csv")
prs = pd.read_csv("data/cleaned/pull_requests_clean.csv")
commits = pd.read_csv("data/cleaned/commits_clean.csv")


# ============================================================
# 2. Convert dates
# ============================================================

issues["created_at"] = pd.to_datetime(issues["created_at"], utc=True)
issues["closed_at"] = pd.to_datetime(issues["closed_at"], utc=True)

prs["created_at"] = pd.to_datetime(prs["created_at"], utc=True)
prs["merged_at"] = pd.to_datetime(prs["merged_at"], utc=True)

commits["commit_date"] = pd.to_datetime(commits["commit_date"], utc=True)


# ============================================================
# 3. Daily timeline
# ============================================================

start = pd.Timestamp("2026-07-09", tz="UTC")
end = pd.Timestamp("2026-09-12", tz="UTC")

dates = pd.date_range(start, end, freq="D")


# ============================================================
# 4. Build daily repository activity
# ============================================================

rows = []

for date in dates:

    issue_created = (
        issues["created_at"].dt.normalize() == date
    ).sum()

    issue_closed = (
        issues["closed_at"].dt.normalize() == date
    ).sum()

    pr_created = (
        prs["created_at"].dt.normalize() == date
    ).sum()

    pr_merged = (
        prs["merged_at"].dt.normalize() == date
    ).sum()

    commit_count = (
        commits["commit_date"].dt.normalize() == date
    ).sum()

    open_issue_backlog = (
        (issues["created_at"].dt.normalize() <= date)
        &
        (
            issues["closed_at"].isna()
            |
            (issues["closed_at"].dt.normalize() > date)
        )
    ).sum()

    open_pr_backlog = (
        (prs["created_at"].dt.normalize() <= date)
        &
        (
            prs["merged_at"].isna()
            |
            (prs["merged_at"].dt.normalize() > date)
        )
    ).sum()

    rows.append(
        {
            "date": date,
            "issues_opened": issue_created,
            "issues_closed": issue_closed,
            "prs_opened": pr_created,
            "prs_merged": pr_merged,
            "commits": commit_count,
            "open_issue_backlog": open_issue_backlog,
            "open_pr_backlog": open_pr_backlog,
        }
    )


df = pd.DataFrame(rows)


# ============================================================
# 5. Current-day derived features
# ============================================================

df["pr_backlog_growth"] = df["open_pr_backlog"].diff()

df["issue_backlog_growth"] = df["open_issue_backlog"].diff()

df["pr_imbalance"] = (
    df["prs_opened"] - df["prs_merged"]
)

df["issue_imbalance"] = (
    df["issues_opened"] - df["issues_closed"]
)


# ============================================================
# 6. Rolling historical features
# ============================================================

rolling_columns = [
    "prs_opened",
    "prs_merged",
    "issues_opened",
    "issues_closed",
    "commits",
    "pr_backlog_growth",
    "issue_backlog_growth",
]

for column in rolling_columns:

    df[f"{column}_rolling_3d"] = (
        df[column].rolling(3).mean()
    )

    df[f"{column}_rolling_7d"] = (
        df[column].rolling(7).mean()
    )


# ============================================================
# 7. FUTURE TARGET
#
# Average open PR backlog during the following 7 days.
# ============================================================

df["future_7d_avg_backlog"] = (
    df["open_pr_backlog"]
    .shift(-1)
    .rolling(7)
    .mean()
    .shift(-6)
)


# ============================================================
# 8. Remove rows without complete historical windows
#    or complete future target.
# ============================================================

df = df.dropna().reset_index(drop=True)


# ============================================================
# 9. Explicit feature list
# ============================================================

feature_columns = [
    "open_pr_backlog",
    "open_issue_backlog",
    "prs_opened",
    "prs_merged",
    "issues_opened",
    "issues_closed",
    "commits",
    "pr_backlog_growth",
    "issue_backlog_growth",
    "pr_imbalance",
    "issue_imbalance",
    "prs_opened_rolling_3d",
    "prs_opened_rolling_7d",
    "prs_merged_rolling_3d",
    "prs_merged_rolling_7d",
    "issues_opened_rolling_3d",
    "issues_opened_rolling_7d",
    "issues_closed_rolling_3d",
    "issues_closed_rolling_7d",
    "commits_rolling_3d",
    "commits_rolling_7d",
    "pr_backlog_growth_rolling_3d",
    "pr_backlog_growth_rolling_7d",
    "issue_backlog_growth_rolling_3d",
    "issue_backlog_growth_rolling_7d",
]


# ============================================================
# 10. Save the exact dataset
# ============================================================

output_path = "data/features/health_forecast_dataset.csv"

df.to_csv(output_path, index=False)


# ============================================================
# 11. Audit
# ============================================================

print("=" * 60)
print("REPORESCUE HEALTH FORECAST DATASET")
print("=" * 60)

print("\nTotal rows:", len(df))

print(
    "Date range:",
    df["date"].min(),
    "to",
    df["date"].max()
)

print("\nTarget:")
print("future_7d_avg_backlog")

print("\nFeature count:", len(feature_columns))

print("\nFEATURES PASSED TO MODEL:")

for number, feature in enumerate(feature_columns, start=1):
    print(f"{number}. {feature}")

print("\nINTENTIONALLY EXCLUDED:")

print("date -> time index")
print(
    "future_7d_avg_backlog -> future target, "
    "therefore not an input feature"
)

print("\nDataset saved to:")
print(output_path)

print("\nFirst 3 rows:")
print(
    df[
        ["date"]
        + feature_columns
        + ["future_7d_avg_backlog"]
    ].head(3).to_string(index=False)
)

print("\nLast 3 rows:")
print(
    df[
        ["date"]
        + feature_columns
        + ["future_7d_avg_backlog"]
    ].tail(3).to_string(index=False)
)