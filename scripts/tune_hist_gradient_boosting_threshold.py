import os
import numpy as np
import pandas as pd

from sklearn.ensemble import HistGradientBoostingClassifier
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
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

TRAIN_PATH = os.path.join(
    BASE_DIR, "data", "ml", "train.csv"
)

VAL_PATH = os.path.join(
    BASE_DIR, "data", "ml", "validation.csv"
)

TEST_PATH = os.path.join(
    BASE_DIR, "data", "ml", "test.csv"
)

PREDICTION_FEATURE_PATH = os.path.join(
    BASE_DIR,
    "data",
    "features",
    "pr_24h_prediction_features.csv"
)

PR_PATH = os.path.join(
    BASE_DIR,
    "data",
    "cleaned",
    "pull_requests_clean.csv"
)

EMBEDDING_PATH = os.path.join(
    BASE_DIR,
    "data",
    "nlp",
    "embeddings",
    "pr_text_embeddings.npy"
)

EMBEDDING_MAP_PATH = os.path.join(
    BASE_DIR,
    "data",
    "nlp",
    "embeddings",
    "embedding_pr_numbers.csv"
)

OUTPUT_PATH = os.path.join(
    BASE_DIR,
    "data", "ml",
    "hist_gradient_boosting_threshold_results.csv"
)

SEARCH_OUTPUT_PATH = os.path.join(
    BASE_DIR,
    "data", "ml",
    "hist_gradient_boosting_threshold_search.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 60)
print("HISTGRADIENTBOOSTING THRESHOLD TUNING")
print("=" * 60)

train = pd.read_csv(TRAIN_PATH)
val = pd.read_csv(VAL_PATH)
test = pd.read_csv(TEST_PATH)

prediction = pd.read_csv(
    PREDICTION_FEATURE_PATH
)

prs = pd.read_csv(
    PR_PATH
)

prs["pr_number"] = (
    prs["pr_number"].astype(int)
)

prs["created_at"] = pd.to_datetime(
    prs["created_at"],
    utc=True
)


print("\nExisting ML splits:")
print("Train:", train.shape)
print("Validation:", val.shape)
print("Test:", test.shape)


# ============================================================
# RECONSTRUCT EXACT TEMPORAL SPLIT
# ============================================================

split_data = prediction[
    [
        "pr_number",
        "bottleneck_label"
    ]
].copy()

split_data["pr_number"] = (
    split_data["pr_number"].astype(int)
)

split_data = split_data.merge(
    prs[
        [
            "pr_number",
            "created_at"
        ]
    ],
    on="pr_number",
    how="left"
)

# Remove censored records
split_data = split_data[
    split_data["bottleneck_label"].notna()
].copy()

# Chronological order
split_data = split_data.sort_values(
    "created_at"
).reset_index(drop=True)


# ============================================================
# RECREATE SPLITS
# ============================================================

total = len(split_data)

train_size = int(
    total * 0.70
)

val_size = int(
    total * 0.15
)

reconstructed_train = split_data.iloc[
    :train_size
].copy()

reconstructed_val = split_data.iloc[
    train_size:
    train_size + val_size
].copy()

reconstructed_test = split_data.iloc[
    train_size + val_size:
].copy()


print("\nReconstructed split sizes:")
print(
    "Train:",
    len(reconstructed_train)
)

print(
    "Validation:",
    len(reconstructed_val)
)

print(
    "Test:",
    len(reconstructed_test)
)


# ============================================================
# SAFETY CHECK
# ============================================================

if (
    len(reconstructed_train) != len(train)
    or
    len(reconstructed_val) != len(val)
    or
    len(reconstructed_test) != len(test)
):

    raise ValueError(
        "Split sizes do not match existing ML files."
    )

print(
    "\n✓ Split sizes match."
)


# ============================================================
# PR NUMBERS
# ============================================================

train_pr_numbers = (
    reconstructed_train[
        "pr_number"
    ].astype(int).values
)

val_pr_numbers = (
    reconstructed_val[
        "pr_number"
    ].astype(int).values
)

test_pr_numbers = (
    reconstructed_test[
        "pr_number"
    ].astype(int).values
)


# ============================================================
# LABEL CHECK
# ============================================================

if not np.array_equal(
    reconstructed_train[
        "bottleneck_label"
    ].astype(int).values,
    train[
        "bottleneck_label"
    ].astype(int).values
):

    raise ValueError(
        "Train labels do not match."
    )


if not np.array_equal(
    reconstructed_val[
        "bottleneck_label"
    ].astype(int).values,
    val[
        "bottleneck_label"
    ].astype(int).values
):

    raise ValueError(
        "Validation labels do not match."
    )


if not np.array_equal(
    reconstructed_test[
        "bottleneck_label"
    ].astype(int).values,
    test[
        "bottleneck_label"
    ].astype(int).values
):

    raise ValueError(
        "Test labels do not match."
    )


print("✓ Train labels match.")
print("✓ Validation labels match.")
print("✓ Test labels match.")


# ============================================================
# LOAD EMBEDDINGS
# ============================================================

embeddings = np.load(
    EMBEDDING_PATH
)

embedding_map = pd.read_csv(
    EMBEDDING_MAP_PATH
)

embedding_map["pr_number"] = (
    embedding_map["pr_number"].astype(int)
)


if len(embeddings) != len(
    embedding_map
):

    raise ValueError(
        "Embedding matrix and mapping size mismatch."
    )


embedding_lookup = {
    int(pr): embeddings[i]
    for i, pr in enumerate(
        embedding_map["pr_number"]
    )
}


def get_embeddings(pr_numbers):

    vectors = []
    missing = []

    for pr in pr_numbers:

        pr = int(pr)

        if pr not in embedding_lookup:

            missing.append(pr)

        else:

            vectors.append(
                embedding_lookup[pr]
            )

    if missing:

        raise ValueError(
            f"Missing embeddings for "
            f"{len(missing)} PRs.\n"
            f"Examples: {missing[:10]}"
        )

    return np.asarray(
        vectors,
        dtype=np.float32
    )


train_embeddings = get_embeddings(
    train_pr_numbers
)

val_embeddings = get_embeddings(
    val_pr_numbers
)

test_embeddings = get_embeddings(
    test_pr_numbers
)


print("\nEmbedding shapes:")
print(
    "Train:",
    train_embeddings.shape
)

print(
    "Validation:",
    val_embeddings.shape
)

print(
    "Test:",
    test_embeddings.shape
)


# ============================================================
# STRUCTURED FEATURES
# ============================================================

structured_features = [
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


X_train_struct = train[
    structured_features
].copy()

X_val_struct = val[
    structured_features
].copy()

X_test_struct = test[
    structured_features
].copy()


# ============================================================
# TARGET
# ============================================================

y_train = train[
    "bottleneck_label"
].astype(int).values

y_val = val[
    "bottleneck_label"
].astype(int).values

y_test = test[
    "bottleneck_label"
].astype(int).values


# ============================================================
# COMBINE FEATURES
# ============================================================

X_train = np.hstack([
    X_train_struct.values,
    train_embeddings
])

X_val = np.hstack([
    X_val_struct.values,
    val_embeddings
])

X_test = np.hstack([
    X_test_struct.values,
    test_embeddings
])


print("\nFinal feature dimensions:")
print(
    "Train:",
    X_train.shape
)

print(
    "Validation:",
    X_val.shape
)

print(
    "Test:",
    X_test.shape
)


# ============================================================
# TRAIN MODEL
# ============================================================

print(
    "\nTraining HistGradientBoosting..."
)

model = HistGradientBoostingClassifier(
    max_iter=300,
    learning_rate=0.05,
    max_leaf_nodes=31,
    l2_regularization=1.0,
    random_state=42
)

model.fit(
    X_train,
    y_train
)

print(
    "Training completed."
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
# THRESHOLD SEARCH — VALIDATION ONLY
# ============================================================

print(
    "\nSearching thresholds using VALIDATION only..."
)

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

    accuracy = accuracy_score(
        y_val,
        val_predictions
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

threshold_df.to_csv(
    SEARCH_OUTPUT_PATH,
    index=False
)


# ============================================================
# SELECT BEST VALIDATION THRESHOLD
# ============================================================

best_row = threshold_df.loc[
    threshold_df["f1"].idxmax()
]

best_threshold = float(
    best_row["threshold"]
)


print(
    "\nBest validation threshold:",
    f"{best_threshold:.2f}"
)

print(
    f"Validation Accuracy : "
    f"{best_row['accuracy']:.4f}"
)

print(
    f"Validation Precision: "
    f"{best_row['precision']:.4f}"
)

print(
    f"Validation Recall   : "
    f"{best_row['recall']:.4f}"
)

print(
    f"Validation F1       : "
    f"{best_row['f1']:.4f}"
)


# ============================================================
# APPLY FROZEN THRESHOLD TO TEST
# ============================================================

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


# ============================================================
# PRINT TEST RESULTS
# ============================================================

print(
    "\n" + "-" * 50
)

print(
    "HISTGRADIENTBOOSTING - "
    "THRESHOLD-TUNED TEST"
)

print(
    "-" * 50
)

print(
    f"Threshold: {best_threshold:.2f}"
)

print(
    f"Accuracy : {test_accuracy:.4f}"
)

print(
    f"Precision: {test_precision:.4f}"
)

print(
    f"Recall   : {test_recall:.4f}"
)

print(
    f"F1 Score : {test_f1:.4f}"
)

print(
    f"ROC-AUC  : {test_roc_auc:.4f}"
)

print(
    "\nConfusion Matrix:"
)

print(test_cm)


# ============================================================
# SAVE FINAL RESULT
# ============================================================

final_result = pd.DataFrame([
    {
        "model": "HistGradientBoosting - threshold tuned",
        "threshold": best_threshold,
        "validation_f1": best_row["f1"],
        "validation_precision": best_row["precision"],
        "validation_recall": best_row["recall"],
        "test_accuracy": test_accuracy,
        "test_precision": test_precision,
        "test_recall": test_recall,
        "test_f1": test_f1,
        "test_roc_auc": test_roc_auc,
        "tn": test_cm[0, 0],
        "fp": test_cm[0, 1],
        "fn": test_cm[1, 0],
        "tp": test_cm[1, 1]
    }
])

final_result.to_csv(
    OUTPUT_PATH,
    index=False
)


print(
    "\n" + "=" * 60
)

print(
    "RESULTS SAVED"
)

print(
    OUTPUT_PATH
)

print(
    SEARCH_OUTPUT_PATH
)

print(
    "\nExperiment completed successfully."
)