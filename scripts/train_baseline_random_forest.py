import pandas as pd
import numpy as np

from pathlib import Path

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)

# ============================================
# REPORESCUE - BASELINE RANDOM FOREST
# ============================================

BASE_DIR = Path(__file__).resolve().parent.parent

TRAIN_FILE = (
    BASE_DIR
    / "data"
    / "ml"
    / "train.csv"
)

VAL_FILE = (
    BASE_DIR
    / "data"
    / "ml"
    / "validation.csv"
)

TEST_FILE = (
    BASE_DIR
    / "data"
    / "ml"
    / "test.csv"
)

print("=" * 60)
print("REPORESCUE - BASELINE RANDOM FOREST")
print("=" * 60)

# ============================================
# 1. LOAD DATA
# ============================================

train = pd.read_csv(TRAIN_FILE)
validation = pd.read_csv(VAL_FILE)
test = pd.read_csv(TEST_FILE)

print("\nDataset sizes:")
print(f"Train      : {len(train)}")
print(f"Validation : {len(validation)}")
print(f"Test       : {len(test)}")

# ============================================
# 2. SEPARATE FEATURES AND TARGET
# ============================================

TARGET = "bottleneck_label"

X_train = train.drop(
    columns=[TARGET]
)

y_train = train[TARGET]

X_val = validation.drop(
    columns=[TARGET]
)

y_val = validation[TARGET]

X_test = test.drop(
    columns=[TARGET]
)

y_test = test[TARGET]

print("\nFeatures:")
print(f"Number of features: {X_train.shape[1]}")

print("\nFeature names:")

for feature in X_train.columns:
    print(f" - {feature}")

# ============================================
# 3. CREATE BASELINE RANDOM FOREST
# ============================================

print("\n" + "=" * 60)
print("TRAINING RANDOM FOREST")
print("=" * 60)

model = RandomForestClassifier(
    n_estimators=300,
    random_state=42,
    class_weight="balanced",
    n_jobs=-1
)

model.fit(
    X_train,
    y_train
)

print("Training completed.")

# ============================================
# 4. EVALUATION FUNCTION
# ============================================

def evaluate_model(
    model,
    X,
    y,
    dataset_name
):

    predictions = model.predict(X)

    probabilities = model.predict_proba(X)[:, 1]

    accuracy = accuracy_score(
        y,
        predictions
    )

    precision = precision_score(
        y,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        y,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        y,
        predictions,
        zero_division=0
    )

    roc_auc = roc_auc_score(
        y,
        probabilities
    )

    cm = confusion_matrix(
        y,
        predictions
    )

    print("\n" + "=" * 60)
    print(f"{dataset_name} RESULTS")
    print("=" * 60)

    print(
        f"\nAccuracy  : {accuracy:.4f}"
    )

    print(
        f"Precision : {precision:.4f}"
    )

    print(
        f"Recall    : {recall:.4f}"
    )

    print(
        f"F1 Score  : {f1:.4f}"
    )

    print(
        f"ROC-AUC   : {roc_auc:.4f}"
    )

    print("\nConfusion Matrix:")

    print(cm)

    print("\nClassification Report:")

    print(
        classification_report(
            y,
            predictions,
            target_names=[
                "Not Bottleneck",
                "Bottleneck"
            ],
            zero_division=0
        )
    )

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "roc_auc": roc_auc
    }


# ============================================
# 5. EVALUATE TRAINING DATA
# ============================================

train_results = evaluate_model(
    model,
    X_train,
    y_train,
    "TRAIN"
)

# ============================================
# 6. EVALUATE VALIDATION DATA
# ============================================

val_results = evaluate_model(
    model,
    X_val,
    y_val,
    "VALIDATION"
)

# ============================================
# 7. EVALUATE TEST DATA
# ============================================

test_results = evaluate_model(
    model,
    X_test,
    y_test,
    "TEST"
)

# ============================================
# 8. FEATURE IMPORTANCE
# ============================================

print("\n" + "=" * 60)
print("FEATURE IMPORTANCE")
print("=" * 60)

importance = pd.DataFrame({
    "feature": X_train.columns,
    "importance": model.feature_importances_
})

importance = importance.sort_values(
    "importance",
    ascending=False
)

print(
    importance.to_string(
        index=False
    )
)

# ============================================
# 9. FINAL SUMMARY
# ============================================

print("\n" + "=" * 60)
print("BASELINE MODEL SUMMARY")
print("=" * 60)

print(
    f"\nValidation F1     : "
    f"{val_results['f1']:.4f}"
)

print(
    f"Validation ROC-AUC: "
    f"{val_results['roc_auc']:.4f}"
)

print(
    f"\nTest F1           : "
    f"{test_results['f1']:.4f}"
)

print(
    f"Test ROC-AUC      : "
    f"{test_results['roc_auc']:.4f}"
)

print("\nBaseline Random Forest completed.")
print("=" * 60)