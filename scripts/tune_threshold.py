import os
import numpy as np
import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix
)

# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

EMBEDDING_PATH = os.path.join(
    BASE_DIR,
    "data",
    "nlp",
    "embeddings",
    "pr_text_embeddings.npy"
)

EMBEDDING_IDS_PATH = os.path.join(
    BASE_DIR,
    "data",
    "nlp",
    "embeddings",
    "embedding_pr_numbers.csv"
)

FEATURES_PATH = os.path.join(
    BASE_DIR,
    "data",
    "features",
    "pr_24h_prediction_features.csv"
)

PR_CLEAN_PATH = os.path.join(
    BASE_DIR,
    "data",
    "preprocessed",
    "pull_requests_preprocessed.csv"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "data",
    "ml"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# SETTINGS
# ============================================================

STRUCTURED_FEATURES = [
    "title_length",
    "body_length",
    "title_word_count",
    "body_word_count",
    "is_draft",
    "commits_24h",
    "commit_authors_24h",
    "files_changed_24h",
    "additions_24h",
    "deletions_24h",
    "total_changes_24h",
    "changes_per_commit_24h",
    "files_per_commit_24h",
    "deletion_ratio_24h",
    "has_commit_activity_24h",
    "has_file_activity_24h"
]

TARGET = "bottleneck_label"

TRAIN_SIZE = 3393
VAL_SIZE = 727
TEST_SIZE = 728

# ============================================================
# LOAD
# ============================================================

print("=" * 70)
print("VALIDATION-BASED THRESHOLD TUNING")
print("=" * 70)

embeddings = np.load(EMBEDDING_PATH)

embedding_ids = pd.read_csv(
    EMBEDDING_IDS_PATH
)

features = pd.read_csv(
    FEATURES_PATH
)

pr_clean = pd.read_csv(
    PR_CLEAN_PATH
)

print("\nEmbeddings:", embeddings.shape)
print("Features:", len(features))

# ============================================================
# PREPARE TEMPORAL DATA
# ============================================================

pr_clean["created_at"] = pd.to_datetime(
    pr_clean["created_at"],
    utc=True
)

metadata = pr_clean[
    ["pr_number", "created_at"]
].copy()

data = features.merge(
    metadata,
    on="pr_number",
    how="inner"
)

data = data.sort_values(
    "created_at"
).reset_index(drop=True)

if len(data) != TRAIN_SIZE + VAL_SIZE + TEST_SIZE:
    raise ValueError(
        f"Expected {TRAIN_SIZE + VAL_SIZE + TEST_SIZE} rows, "
        f"found {len(data)}."
    )

train_data = data.iloc[
    :TRAIN_SIZE
].copy()

val_data = data.iloc[
    TRAIN_SIZE:TRAIN_SIZE + VAL_SIZE
].copy()

test_data = data.iloc[
    TRAIN_SIZE + VAL_SIZE:
].copy()

print("\nTemporal split:")
print("Train:", len(train_data))
print("Validation:", len(val_data))
print("Test:", len(test_data))

# ============================================================
# EMBEDDING MAPPING
# ============================================================

embedding_ids["pr_number"] = (
    embedding_ids["pr_number"].astype(int)
)

embedding_map = {
    pr_number: index
    for index, pr_number
    in enumerate(
        embedding_ids["pr_number"]
    )
}

def get_embeddings(split_data):

    indices = []

    for pr_number in split_data["pr_number"]:

        if pr_number not in embedding_map:
            raise ValueError(
                f"Missing embedding for PR #{pr_number}"
            )

        indices.append(
            embedding_map[pr_number]
        )

    return embeddings[indices]

# ============================================================
# GET EMBEDDINGS
# ============================================================

train_embeddings = get_embeddings(train_data)
val_embeddings = get_embeddings(val_data)
test_embeddings = get_embeddings(test_data)

# ============================================================
# STRUCTURED FEATURES
# ============================================================

X_train_structured = (
    train_data[STRUCTURED_FEATURES]
    .astype(float)
    .values
)

X_val_structured = (
    val_data[STRUCTURED_FEATURES]
    .astype(float)
    .values
)

X_test_structured = (
    test_data[STRUCTURED_FEATURES]
    .astype(float)
    .values
)

y_train = (
    train_data[TARGET]
    .astype(int)
    .values
)

y_val = (
    val_data[TARGET]
    .astype(int)
    .values
)

y_test = (
    test_data[TARGET]
    .astype(int)
    .values
)

# ============================================================
# SCALE STRUCTURED FEATURES
# ============================================================

print("\nScaling structured features...")

scaler = StandardScaler()

X_train_structured = scaler.fit_transform(
    X_train_structured
)

X_val_structured = scaler.transform(
    X_val_structured
)

X_test_structured = scaler.transform(
    X_test_structured
)

# ============================================================
# COMBINE
# ============================================================

X_train = np.hstack([
    X_train_structured,
    train_embeddings
])

X_val = np.hstack([
    X_val_structured,
    val_embeddings
])

X_test = np.hstack([
    X_test_structured,
    test_embeddings
])

print("\nFinal feature dimensions:")
print("Train:", X_train.shape)
print("Validation:", X_val.shape)
print("Test:", X_test.shape)

# ============================================================
# TRAIN MODEL
# ============================================================

print("\nTraining Logistic Regression...")

model = LogisticRegression(
    max_iter=3000,
    class_weight="balanced",
    random_state=42
)

model.fit(
    X_train,
    y_train
)

print(
    "Iterations:",
    model.n_iter_[0]
)

# ============================================================
# GET PROBABILITIES
# ============================================================

val_probabilities = (
    model.predict_proba(X_val)[:, 1]
)

test_probabilities = (
    model.predict_proba(X_test)[:, 1]
)

# ============================================================
# THRESHOLD SEARCH ON VALIDATION ONLY
# ============================================================

print("\nSearching thresholds using VALIDATION only...")

thresholds = np.arange(
    0.10,
    0.91,
    0.01
)

threshold_results = []

for threshold in thresholds:

    val_predictions = (
        val_probabilities >= threshold
    ).astype(int)

    accuracy = accuracy_score(
        y_val,
        val_predictions
    )

    precision = precision_score(
        y_val,
        val_predictions,
        zero_division=0
    )

    recall = recall_score(
        y_val,
        val_predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_val,
        val_predictions,
        zero_division=0
    )

    threshold_results.append({
        "threshold": threshold,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1
    })

threshold_df = pd.DataFrame(
    threshold_results
)

# ============================================================
# FIND BEST VALIDATION F1
# ============================================================

best_row = threshold_df.loc[
    threshold_df["f1"].idxmax()
]

best_threshold = float(
    best_row["threshold"]
)

print("\n" + "=" * 70)
print("BEST VALIDATION THRESHOLD")
print("=" * 70)

print(
    f"Threshold : {best_threshold:.2f}"
)

print(
    f"Accuracy  : {best_row['accuracy']:.4f}"
)

print(
    f"Precision : {best_row['precision']:.4f}"
)

print(
    f"Recall    : {best_row['recall']:.4f}"
)

print(
    f"F1 Score  : {best_row['f1']:.4f}"
)

# ============================================================
# FINAL TEST EVALUATION
# ============================================================

print("\nApplying selected threshold to TEST...")

test_predictions = (
    test_probabilities >= best_threshold
).astype(int)

test_accuracy = accuracy_score(
    y_test,
    test_predictions
)

test_precision = precision_score(
    y_test,
    test_predictions,
    zero_division=0
)

test_recall = recall_score(
    y_test,
    test_predictions,
    zero_division=0
)

test_f1 = f1_score(
    y_test,
    test_predictions,
    zero_division=0
)

test_roc_auc = roc_auc_score(
    y_test,
    test_probabilities
)

test_cm = confusion_matrix(
    y_test,
    test_predictions
)

print("\n" + "=" * 70)
print("FINAL TEST RESULT")
print("=" * 70)

print(
    f"Threshold : {best_threshold:.2f}"
)

print(
    f"Accuracy  : {test_accuracy:.4f}"
)

print(
    f"Precision : {test_precision:.4f}"
)

print(
    f"Recall    : {test_recall:.4f}"
)

print(
    f"F1 Score  : {test_f1:.4f}"
)

print(
    f"ROC-AUC   : {test_roc_auc:.4f}"
)

print("\nConfusion Matrix:")
print(test_cm)

# ============================================================
# SAVE THRESHOLD RESULTS
# ============================================================

threshold_path = os.path.join(
    OUTPUT_DIR,
    "threshold_search_results.csv"
)

threshold_df.to_csv(
    threshold_path,
    index=False
)

# ============================================================
# SAVE FINAL SUMMARY
# ============================================================

summary = pd.DataFrame([{
    "selected_threshold": best_threshold,
    "validation_f1": best_row["f1"],
    "validation_precision": best_row["precision"],
    "validation_recall": best_row["recall"],
    "test_accuracy": test_accuracy,
    "test_precision": test_precision,
    "test_recall": test_recall,
    "test_f1": test_f1,
    "test_roc_auc": test_roc_auc
}])

summary_path = os.path.join(
    OUTPUT_DIR,
    "threshold_tuned_results.csv"
)

summary.to_csv(
    summary_path,
    index=False
)

print("\nSaved:")
print(threshold_path)
print(summary_path)

print("\n" + "=" * 70)
print("THRESHOLD TUNING FINISHED")
print("=" * 70)