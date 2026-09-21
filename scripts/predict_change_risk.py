import os
import joblib
import pandas as pd

BASE = "data/ml"
ARTIFACTS = os.path.join(BASE, "model_artifacts")

MODEL = joblib.load(os.path.join(ARTIFACTS, "change_risk_model.joblib"))
SCALER = joblib.load(os.path.join(ARTIFACTS, "change_risk_scaler.joblib"))
FEATURES = joblib.load(os.path.join(ARTIFACTS, "change_risk_features.joblib"))
CONFIG = joblib.load(os.path.join(ARTIFACTS, "change_risk_config.joblib"))

DATA = pd.read_csv(os.path.join(BASE, "change_risk_ml_dataset.csv"))

def predict_change_risk(pr_number):

    row = DATA[DATA["pr_number"] == pr_number]

    if row.empty:
        return {
            "success": False,
            "error": f"No Change-Risk data available for PR #{pr_number}"
        }

    X = row[FEATURES]
    X_scaled = SCALER.transform(X)

    probability = float(MODEL.predict_proba(X_scaled)[0, 1])
    threshold = float(CONFIG["threshold"])

    prediction = (
        "High Change Risk"
        if probability >= threshold
        else "Lower Change Risk"
    )

    evidence = []

    if row["total_changes_24h"].iloc[0] > 0:
        evidence.append("Code changes observed in first 24h")

    if row["files_changed_24h"].iloc[0] > 0:
        evidence.append("Files changed in first 24h")

    if row["commits_24h"].iloc[0] > 0:
        evidence.append("Commit activity observed in first 24h")

    if row["commit_authors_24h"].iloc[0] > 1:
        evidence.append("Multiple contributing developers")

    if row["is_draft"].iloc[0]:
        evidence.append("PR is currently a draft")

    if row["deletion_ratio_24h"].iloc[0] > 0.5:
        evidence.append("High deletion ratio in first 24h")

    return {
        "success": True,
        "pr_number": int(pr_number),
        "probability": probability,
        "probability_percent": round(probability * 100, 2),
        "prediction": prediction,
        "threshold": threshold,
        "top_evidence": evidence[:6],
        "feature_count": len(FEATURES)
    }


if __name__ == "__main__":

    for pr in [333333, 333999, 326789]:

        result = predict_change_risk(pr)

        print("=" * 60)
        print(f"PR #{pr}")
        print(result)
