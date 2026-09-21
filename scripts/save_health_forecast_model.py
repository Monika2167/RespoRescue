from pathlib import Path
import joblib
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge


# ============================================================
# REPORESCUE — SAVE REPOSITORY HEALTH FORECAST MODEL
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATASET_PATH = BASE_DIR / "data" / "features" / "health_forecast_dataset.csv"
ARTIFACT_DIR = BASE_DIR / "data" / "ml" / "model_artifacts"

ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 1. LOAD DATASET
# ============================================================

df = pd.read_csv(DATASET_PATH)

df["date"] = pd.to_datetime(df["date"], utc=True)

print("=" * 65)
print("REPORESCUE — SAVE REPOSITORY HEALTH FORECAST MODEL")
print("=" * 65)

print("\nSOURCE DATASET:")
print(DATASET_PATH)

print("\nSOURCE COLUMNS:")
print(df.columns.tolist())


# ============================================================
# 2. EXPLICIT FEATURE LIST
# ============================================================

FEATURES = [
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

TARGET = "future_7d_avg_backlog"


# ============================================================
# 3. FEATURE AUDIT
# ============================================================

print("\nFEATURES ACTUALLY PASSED TO MODEL:")

for i, feature in enumerate(FEATURES, start=1):
    print(f"{i}. {feature}")

print(f"\nFEATURE COUNT: {len(FEATURES)}")

print("\nINTENTIONALLY EXCLUDED:")
print("date -> time index")
print(f"{TARGET} -> future target")


# ============================================================
# 4. VERIFY COLUMNS
# ============================================================

missing_features = [
    feature for feature in FEATURES
    if feature not in df.columns
]

if missing_features:
    raise ValueError(
        f"Missing required features: {missing_features}"
    )

if TARGET not in df.columns:
    raise ValueError(
        f"Target column '{TARGET}' not found."
    )


# ============================================================
# 5. CHRONOLOGICAL SORT
# ============================================================

df = df.sort_values("date").reset_index(drop=True)


# ============================================================
# 6. BUILD X AND y
# ============================================================

X = df[FEATURES].copy()
y = df[TARGET].copy()


# ============================================================
# 7. DATA QUALITY CHECK
# ============================================================

print("\n" + "=" * 65)
print("DATA QUALITY CHECK")
print("=" * 65)

print(
    "Missing feature values:",
    int(X.isna().sum().sum())
)

print(
    "Infinite feature values:",
    int(X.isin([float("inf"), float("-inf")]).sum().sum())
)

if X.isna().any().any():
    raise ValueError("Missing feature values detected.")

if X.isin([float("inf"), float("-inf")]).any().any():
    raise ValueError("Infinite feature values detected.")


# ============================================================
# 8. CHRONOLOGICAL SPLIT
# ============================================================

train_size = 31
validation_size = 10

X_train = X.iloc[:train_size]
X_validation = X.iloc[
    train_size:train_size + validation_size
]
X_test = X.iloc[
    train_size + validation_size:
]

y_train = y.iloc[:train_size]
y_validation = y.iloc[
    train_size:train_size + validation_size
]
y_test = y.iloc[
    train_size + validation_size:
]

print("\n" + "=" * 65)
print("CHRONOLOGICAL SPLIT")
print("=" * 65)

print(
    "TRAIN:",
    len(X_train),
    df["date"].iloc[0],
    "to",
    df["date"].iloc[train_size - 1]
)

print(
    "VALIDATION:",
    len(X_validation),
    df["date"].iloc[train_size],
    "to",
    df["date"].iloc[train_size + validation_size - 1]
)

print(
    "TEST:",
    len(X_test),
    df["date"].iloc[train_size + validation_size],
    "to",
    df["date"].iloc[-1]
)


# ============================================================
# 9. SCALE FEATURES
# ============================================================

scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)

X_validation_scaled = scaler.transform(X_validation)

X_test_scaled = scaler.transform(X_test)


# ============================================================
# 10. VALIDATION-SELECTED ALPHA
# ============================================================

SELECTED_ALPHA = 0.01

model = Ridge(alpha=SELECTED_ALPHA)

model.fit(X_train_scaled, y_train)


# ============================================================
# 11. SAVE ARTIFACTS
# ============================================================

model_path = (
    ARTIFACT_DIR /
    "health_forecast_model.joblib"
)

scaler_path = (
    ARTIFACT_DIR /
    "health_forecast_scaler.joblib"
)

features_path = (
    ARTIFACT_DIR /
    "health_forecast_features.joblib"
)

config_path = (
    ARTIFACT_DIR /
    "health_forecast_config.joblib"
)


joblib.dump(model, model_path)

joblib.dump(scaler, scaler_path)

joblib.dump(FEATURES, features_path)

joblib.dump(
    {
        "target": TARGET,
        "alpha": SELECTED_ALPHA,
        "train_size": train_size,
        "validation_size": validation_size,
        "feature_count": len(FEATURES),
        "prediction_type": (
            "Future 7-day average open PR backlog"
        ),
    },
    config_path,
)


# ============================================================
# 12. VERIFY SAVED FILES
# ============================================================

print("\n" + "=" * 65)
print("MODEL ARTIFACTS SAVED")
print("=" * 65)

print(model_path)
print(scaler_path)
print(features_path)
print(config_path)

print("\n" + "=" * 65)
print("SUCCESS")
print("=" * 65)

print(
    f"Model: Ridge Regression "
    f"(alpha={SELECTED_ALPHA})"
)

print(f"Features: {len(FEATURES)}")

print("Scaling: StandardScaler")

print(
    "Artifacts successfully saved "
    "for API integration."
)