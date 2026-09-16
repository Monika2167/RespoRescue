import os
import pandas as pd

from scipy.sparse import load_npz
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NLP_DIR = os.path.join(BASE_DIR, "data", "nlp")
ML_DIR = os.path.join(BASE_DIR, "data", "ml")


# ============================================================
# LOAD TF-IDF MATRICES
# ============================================================

print("=" * 60)
print("REPORESCUE - TF-IDF BASELINE")
print("=" * 60)

X_train = load_npz(
    os.path.join(NLP_DIR, "tfidf_train.npz")
)

X_validation = load_npz(
    os.path.join(NLP_DIR, "tfidf_validation.npz")
)

X_test = load_npz(
    os.path.join(NLP_DIR, "tfidf_test.npz")
)


# ============================================================
# LOAD TARGETS
# ============================================================

train = pd.read_csv(
    os.path.join(ML_DIR, "train.csv")
)

validation = pd.read_csv(
    os.path.join(ML_DIR, "validation.csv")
)

test = pd.read_csv(
    os.path.join(ML_DIR, "test.csv")
)

y_train = train["bottleneck_label"]
y_validation = validation["bottleneck_label"]
y_test = test["bottleneck_label"]


# ============================================================
# DATASET INFORMATION
# ============================================================

print("\nDataset sizes:")
print(f"Train      : {X_train.shape[0]}")
print(f"Validation : {X_validation.shape[0]}")
print(f"Test       : {X_test.shape[0]}")

print(f"\nTF-IDF dimensions: {X_train.shape[1]}")


# ============================================================
# TRAIN LOGISTIC REGRESSION
# ============================================================

print("\n" + "=" * 60)
print("TRAINING TF-IDF LOGISTIC REGRESSION")
print("=" * 60)

model = LogisticRegression(
    max_iter=2000,
    class_weight="balanced",
    random_state=42
)

model.fit(X_train, y_train)

print("Training completed.")


# ============================================================
# EVALUATION FUNCTION
# ============================================================

def evaluate_model(name, X, y):

    predictions = model.predict(X)
    probabilities = model.predict_proba(X)[:, 1]

    accuracy = accuracy_score(y, predictions)
    precision = precision_score(
        y, predictions, zero_division=0
    )
    recall = recall_score(
        y, predictions, zero_division=0
    )
    f1 = f1_score(
        y, predictions, zero_division=0
    )
    roc_auc = roc_auc_score(
        y, probabilities
    )

    cm = confusion_matrix(y, predictions)

    print("\n" + "=" * 60)
    print(f"{name} RESULTS")
    print("=" * 60)

    print(f"\nAccuracy  : {accuracy:.4f}")
    print(f"Precision : {precision:.4f}")
    print(f"Recall    : {recall:.4f}")
    print(f"F1 Score  : {f1:.4f}")
    print(f"ROC-AUC   : {roc_auc:.4f}")

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


# ============================================================
# EVALUATE
# ============================================================

train_results = evaluate_model(
    "TRAIN",
    X_train,
    y_train
)

validation_results = evaluate_model(
    "VALIDATION",
    X_validation,
    y_validation
)

test_results = evaluate_model(
    "TEST",
    X_test,
    y_test
)


# ============================================================
# TOP POSITIVE / NEGATIVE WORDS
# ============================================================

print("\n" + "=" * 60)
print("TOP NLP SIGNALS")
print("=" * 60)

vocabulary = pd.read_csv(
    os.path.join(
        NLP_DIR,
        "tfidf_vocabulary.csv"
    )
)

terms = vocabulary["term"].values

coefficients = model.coef_[0]

top_positive_indices = coefficients.argsort()[-20:][::-1]

top_negative_indices = coefficients.argsort()[:20]


print("\nTerms associated with BOTTLENECK:")
for index in top_positive_indices:
    print(
        f"{terms[index]:30s} "
        f"{coefficients[index]:.4f}"
    )


print("\nTerms associated with NOT BOTTLENECK:")
for index in top_negative_indices:
    print(
        f"{terms[index]:30s} "
        f"{coefficients[index]:.4f}"
    )


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("TF-IDF BASELINE SUMMARY")
print("=" * 60)

print(
    f"\nValidation F1     : "
    f"{validation_results['f1']:.4f}"
)

print(
    f"Validation ROC-AUC: "
    f"{validation_results['roc_auc']:.4f}"
)

print(
    f"\nTest F1           : "
    f"{test_results['f1']:.4f}"
)

print(
    f"Test ROC-AUC      : "
    f"{test_results['roc_auc']:.4f}"
)

print("\nTF-IDF baseline completed.")
print("=" * 60)