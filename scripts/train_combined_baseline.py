import os
import numpy as np
import pandas as pd

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
# LOAD DATA
# ============================================================

print("=" * 65)
print("COMBINED STRUCTURED + SEMANTIC MODEL")
print("=" * 65)

print("\nLoading data...")

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

print("Embeddings :", embeddings.shape)
print("Feature rows:", len(features))

# ============================================================
# IDENTIFY STRUCTURED FEATURES
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

# Verify columns
missing_features = [
    col for col in STRUCTURED_FEATURES
    if col not in features.columns
]

if missing_features:
    raise ValueError(
        f"Missing structured features: {missing_features}"
    )

# ============================================================
# PREPARE METADATA
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

# ============================================================
# TEMPORAL ORDER
# ============================================================

data = data.sort_values(
    "created_at"
).reset_index(drop=True)

print("\nTotal labeled PRs:", len(data))

# Same split used in previous experiments
TRAIN_SIZE = 3393
VAL_SIZE = 727
TEST_SIZE = 728

if len(data) != TRAIN_SIZE + VAL_SIZE + TEST_SIZE:
    raise ValueError(
        "Dataset size does not match the established "
        "temporal split."
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
print("Train      :", len(train_data))
print("Validation :", len(val_data))
print("Test       :", len(test_data))

# ============================================================
# EMBEDDING MAPPING
# ============================================================

embedding_ids["pr_number"] = (
    embedding_ids["pr_number"]
    .astype(int)
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
                f"Embedding missing for PR #{pr_number}"
            )

        indices.append(
            embedding_map[pr_number]
        )

    return embeddings[indices]


# ============================================================
# GET EMBEDDINGS
# ============================================================

train_embeddings = get_embeddings(
    train_data
)

val_embeddings = get_embeddings(
    val_data
)

test_embeddings = get_embeddings(
    test_data
)

# ============================================================
# GET STRUCTURED FEATURES
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

# ============================================================
# COMBINE FEATURES
# ============================================================

print("\nCombining structured + semantic features...")

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

print("\nCombined feature dimensions:")
print("X_train:", X_train.shape)
print("X_val  :", X_val.shape)
print("X_test :", X_test.shape)

# ============================================================
# CHECK DATA
# ============================================================

if not np.isfinite(X_train).all():
    raise ValueError(
        "X_train contains NaN or infinite values."
    )

if not np.isfinite(X_val).all():
    raise ValueError(
        "X_val contains NaN or infinite values."
    )

if not np.isfinite(X_test).all():
    raise ValueError(
        "X_test contains NaN or infinite values."
    )

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

print("Training complete.")

# ============================================================
# EVALUATION
# ============================================================

def evaluate(
    dataset_name,
    X,
    y
):

    predictions = model.predict(X)

    probabilities = (
        model.predict_proba(X)[:, 1]
    )

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

    print("\n" + "=" * 65)
    print(dataset_name)
    print("=" * 65)

    print(f"Accuracy  : {accuracy:.4f}")
    print(f"Precision : {precision:.4f}")
    print(f"Recall    : {recall:.4f}")
    print(f"F1 Score  : {f1:.4f}")
    print(f"ROC-AUC   : {roc_auc:.4f}")

    print("\nConfusion Matrix:")
    print(cm)

    return {
        "dataset": dataset_name,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "roc_auc": roc_auc
    }


# ============================================================
# RUN EVALUATION
# ============================================================

train_result = evaluate(
    "TRAIN",
    X_train,
    y_train
)

val_result = evaluate(
    "VALIDATION",
    X_val,
    y_val
)

test_result = evaluate(
    "TEST",
    X_test,
    y_test
)

# ============================================================
# SAVE RESULTS
# ============================================================

results = pd.DataFrame([
    train_result,
    val_result,
    test_result
])

output_path = os.path.join(
    OUTPUT_DIR,
    "combined_baseline_results.csv"
)

results.to_csv(
    output_path,
    index=False
)

print("\nResults saved to:")
print(output_path)

print("\n" + "=" * 65)
print("COMBINED MODEL FINISHED")
print("=" * 65)