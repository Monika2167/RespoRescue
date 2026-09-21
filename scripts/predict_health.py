from pathlib import Path
import joblib
import pandas as pd


# ============================================================
# REPORESCUE — REPOSITORY HEALTH FORECAST PREDICTION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATASET_PATH = (
    BASE_DIR
    / "data"
    / "features"
    / "health_forecast_dataset.csv"
)

ARTIFACT_DIR = (
    BASE_DIR
    / "data"
    / "ml"
    / "model_artifacts"
)

MODEL_PATH = ARTIFACT_DIR / "health_forecast_model.joblib"
SCALER_PATH = ARTIFACT_DIR / "health_forecast_scaler.joblib"
FEATURES_PATH = ARTIFACT_DIR / "health_forecast_features.joblib"
CONFIG_PATH = ARTIFACT_DIR / "health_forecast_config.joblib"


# ============================================================
# LOAD ARTIFACTS
# ============================================================

model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
features = joblib.load(FEATURES_PATH)
config = joblib.load(CONFIG_PATH)


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(DATASET_PATH)

df["date"] = pd.to_datetime(df["date"], utc=True)

df = df.sort_values("date").reset_index(drop=True)


# ============================================================
# FEATURE AUDIT
# ============================================================

missing_features = [
    feature for feature in features
    if feature not in df.columns
]

if missing_features:
    raise ValueError(
        f"Missing required features: {missing_features}"
    )


# ============================================================
# PREDICTION FUNCTION
# ============================================================

def predict_health(date=None):

    # --------------------------------------------------------
    # If no date is provided, use the latest available date
    # --------------------------------------------------------

    if date is None:
        row = df.iloc[[-1]].copy()
    else:

        requested_date = pd.to_datetime(
            date,
            utc=True
        ).normalize()

        matching_rows = df[
            df["date"].dt.normalize() == requested_date
        ]

        if matching_rows.empty:
            return {
                "success": False,
                "error": (
                    f"No health forecast data available "
                    f"for {date}"
                )
            }

        row = matching_rows.iloc[[-1]].copy()

    # --------------------------------------------------------
    # Extract exactly the 25 model features
    # --------------------------------------------------------

    X = row[features].copy()

    # --------------------------------------------------------
    # Data quality check
    # --------------------------------------------------------

    if X.isna().any().any():
        return {
            "success": False,
            "error": "Missing feature values detected."
        }

    if X.isin(
        [float("inf"), float("-inf")]
    ).any().any():

        return {
            "success": False,
            "error": "Infinite feature values detected."
        }

    # --------------------------------------------------------
    # Scale using saved training scaler
    # --------------------------------------------------------

    X_scaled = scaler.transform(X)

    # --------------------------------------------------------
    # Predict
    # --------------------------------------------------------

    prediction = float(
        model.predict(X_scaled)[0]
    )

    # Backlog cannot be negative
    prediction = max(0.0, prediction)

    # --------------------------------------------------------
    # Current repository state
    # --------------------------------------------------------

    current_pr_backlog = float(
        row["open_pr_backlog"].iloc[0]
    )

    current_issue_backlog = float(
        row["open_issue_backlog"].iloc[0]
    )

    # --------------------------------------------------------
    # Return structured result
    # --------------------------------------------------------

    return {
        "success": True,
        "date": row["date"].iloc[0].isoformat(),
        "forecast": round(prediction, 2),
        "forecast_unit": (
            "average open PR backlog over next 7 days"
        ),
        "current_open_pr_backlog": round(
            current_pr_backlog,
            2
        ),
        "current_open_issue_backlog": round(
            current_issue_backlog,
            2
        ),
        "model": "Ridge Regression",
        "alpha": config["alpha"],
        "feature_count": config["feature_count"],
        "features": features,
    }


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    result = predict_health()

    print("=" * 65)
    print("REPORESCUE — REPOSITORY HEALTH FORECAST")
    print("=" * 65)

    print("\nRESULT:")

    for key, value in result.items():
        print(f"{key}: {value}")