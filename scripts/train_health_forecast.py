import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error


# ============================================================
# 1. Load canonical dataset
# ============================================================

DATA_PATH = "data/features/health_forecast_dataset.csv"

df = pd.read_csv(DATA_PATH)

df["date"] = pd.to_datetime(df["date"], utc=True)


# ============================================================
# 2. Explicit feature list
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

target_column = "future_7d_avg_backlog"


# ============================================================
# 3. Explicit feature audit
# ============================================================

print("=" * 65)
print("REPORESCUE — REPOSITORY HEALTH FORECAST")
print("=" * 65)

print("\nSOURCE DATASET:")
print(DATA_PATH)

print("\nSOURCE COLUMNS:")
print(df.columns.tolist())

print("\nFEATURES ACTUALLY PASSED TO MODEL:")
for number, feature in enumerate(feature_columns, start=1):
    print(f"{number}. {feature}")

print("\nFEATURE COUNT:", len(feature_columns))

print("\nINTENTIONALLY EXCLUDED:")
print("date -> time index")
print(f"{target_column} -> future target")


# ============================================================
# 4. Chronological split
# ============================================================

train = df.iloc[:31].copy()
validation = df.iloc[31:41].copy()
test = df.iloc[41:52].copy()

X_train = train[feature_columns]
y_train = train[target_column]

X_val = validation[feature_columns]
y_val = validation[target_column]

X_test = test[feature_columns]
y_test = test[target_column]


print("\n" + "=" * 65)
print("CHRONOLOGICAL SPLIT")
print("=" * 65)

print(
    "\nTRAIN:",
    len(train),
    train["date"].min(),
    "to",
    train["date"].max(),
)

print(
    "VALIDATION:",
    len(validation),
    validation["date"].min(),
    "to",
    validation["date"].max(),
)

print(
    "TEST:",
    len(test),
    test["date"].min(),
    "to",
    test["date"].max(),
)


# ============================================================
# 5. Check missing/infinite values
# ============================================================

print("\n" + "=" * 65)
print("DATA QUALITY CHECK")
print("=" * 65)

print("Missing feature values:", X_train.isna().sum().sum())
print("Infinite feature values:", np.isinf(X_train.to_numpy()).sum())


# ============================================================
# 6. Scale using TRAIN ONLY
# ============================================================

scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)

X_val_scaled = scaler.transform(X_val)

X_test_scaled = scaler.transform(X_test)


# ============================================================
# 7. Validation model selection
# ============================================================

alphas = [0.01, 0.1, 1.0, 10.0, 100.0, 1000.0]

results = []

print("\n" + "=" * 65)
print("VALIDATION RESULTS")
print("=" * 65)

for alpha in alphas:

    model = Ridge(alpha=alpha)

    model.fit(X_train_scaled, y_train)

    val_prediction = model.predict(X_val_scaled)

    mae = mean_absolute_error(
        y_val,
        val_prediction
    )

    rmse = mean_squared_error(
        y_val,
        val_prediction
    ) ** 0.5

    results.append(
        {
            "alpha": alpha,
            "validation_mae": mae,
            "validation_rmse": rmse,
        }
    )

    print(
        f"alpha={alpha:<7} "
        f"MAE={mae:.2f} "
        f"RMSE={rmse:.2f}"
    )


results_df = pd.DataFrame(results)

best_row = results_df.loc[
    results_df["validation_mae"].idxmin()
]

best_alpha = best_row["alpha"]


print("\nSELECTED ALPHA:", best_alpha)


# ============================================================
# 8. Train selected model
# ============================================================

final_model = Ridge(alpha=best_alpha)

final_model.fit(
    X_train_scaled,
    y_train
)


# ============================================================
# 9. Final untouched test evaluation
# ============================================================

test_prediction = final_model.predict(X_test_scaled)

test_mae = mean_absolute_error(
    y_test,
    test_prediction
)

test_rmse = mean_squared_error(
    y_test,
    test_prediction
) ** 0.5


print("\n" + "=" * 65)
print("FINAL TEST RESULT")
print("=" * 65)

print(f"\nML Test MAE:  {test_mae:.2f}")
print(f"ML Test RMSE: {test_rmse:.2f}")

print("\nFrozen baseline:")
print("Baseline MAE:  112.31")
print("Baseline RMSE: 114.78")


# ============================================================
# 10. Improvement calculation
# ============================================================

baseline_mae = 112.31
baseline_rmse = 114.78

mae_improvement = (
    (baseline_mae - test_mae)
    / baseline_mae
) * 100

rmse_improvement = (
    (baseline_rmse - test_rmse)
    / baseline_rmse
) * 100


print("\n" + "=" * 65)
print("BASELINE COMPARISON")
print("=" * 65)

print(
    f"\nMAE improvement:  {mae_improvement:.2f}%"
)

print(
    f"RMSE improvement: {rmse_improvement:.2f}%"
)


# ============================================================
# 11. Test predictions
# ============================================================

prediction_table = pd.DataFrame(
    {
        "date": test["date"],
        "actual": y_test.values,
        "baseline": test["open_pr_backlog"].values,
        "ml_prediction": test_prediction,
    }
)

prediction_table["ml_error"] = (
    prediction_table["actual"]
    - prediction_table["ml_prediction"]
)

prediction_table["baseline_error"] = (
    prediction_table["actual"]
    - prediction_table["baseline"]
)


print("\n" + "=" * 65)
print("TEST PREDICTIONS")
print("=" * 65)

print(
    prediction_table.round(2).to_string(
        index=False
    )
)


# ============================================================
# 12. Save results
# ============================================================

results_df.to_csv(
    "data/ml/health_forecast_validation_results.csv",
    index=False
)

prediction_table.to_csv(
    "data/ml/health_forecast_test_predictions.csv",
    index=False
)

print("\nResults saved:")
print("data/ml/health_forecast_validation_results.csv")
print("data/ml/health_forecast_test_predictions.csv")