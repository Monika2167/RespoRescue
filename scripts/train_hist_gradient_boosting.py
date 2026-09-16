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
    "data",
    "ml",
    "hist_gradient_boosting_results.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 60)
print("HISTGRADIENTBOOSTING + SEMANTIC EMBEDDING EXPERIMENT")
print("=" * 60)

train = pd.read_csv(TRAIN_PATH)
val = pd.read_csv(VAL_PATH)
test = pd.read_csv(TEST_PATH)

print("\nExisting ML splits:")
print("Train:", train.shape)
print("Validation:", val.shape)
print("Test:", test.shape)


# ============================================================
# LOAD PR DATA FOR EXACT SPLIT RECONSTRUCTION
# ============================================================

prediction = pd.read_csv(
    PREDICTION_FEATURE_PATH
)

prs = pd.read_csv(
    PR_PATH
)

prs["pr_number"] = prs[
    "pr_number"
].astype(int)

prs["created_at"] = pd.to_datetime(
    prs["created_at"],
    utc=True
)

split_data = prediction[
    [
        "pr_number",
        "bottleneck_label"
    ]
].copy()

split_data["pr_number"] = (
    split_data["pr_number"]
    .astype(int)
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

# Remove censored examples
split_data = split_data[
    split_data["bottleneck_label"].notna()
].copy()

# Chronological order
split_data = split_data.sort_values(
    "created_at"
).reset_index(drop=True)


# ============================================================
# RECREATE EXACT 70 / 15 / 15 TEMPORAL SPLIT
# ============================================================

total = len(split_data)

train_size = int(total * 0.70)
val_size = int(total * 0.15)

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
print("Train:", len(reconstructed_train))
print("Validation:", len(reconstructed_val))
print("Test:", len(reconstructed_test))


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
        "Temporal split sizes do not match existing ML files."
    )

print("\n✓ Temporal split sizes match.")


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
# VERIFY LABEL ALIGNMENT
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
    embedding_map["pr_number"]
    .astype(int)
)

print("\nEmbedding matrix:")
print(embeddings.shape)

print(
    "Embedding map:",
    embedding_map.shape
)


# ============================================================
# EMBEDDING LOOKUP
# ============================================================

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
            f"{len(missing)} PRs. "
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


print("\nEmbedding split shapes:")
print("Train:", train_embeddings.shape)
print("Validation:", val_embeddings.shape)
print("Test:", test_embeddings.shape)


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
# COMBINE STRUCTURED + EMBEDDINGS
# ============================================================

X_train = np.hstack(
    [
        X_train_struct.values,
        train_embeddings
    ]
)

X_val = np.hstack(
    [
        X_val_struct.values,
        val_embeddings
    ]
)

X_test = np.hstack(
    [
        X_test_struct.values,
        test_embeddings
    ]
)


print("\nFinal feature dimensions:")
print("Train:", X_train.shape)
print("Validation:", X_val.shape)
print("Test:", X_test.shape)


# ============================================================
# HISTGRADIENTBOOSTING
# ============================================================

print(
    "\nTraining HistGradientBoostingClassifier..."
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
# EVALUATION
# ============================================================

def evaluate_model(
    name,
    X,
    y
):

    probabilities = (
        model.predict_proba(X)[:, 1]
    )

    predictions = (
        probabilities >= 0.5
    ).astype(int)

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

    print(
        "\n" + "-" * 50
    )

    print(name)

    print(
        "-" * 50
    )

    print(
        f"Accuracy : {accuracy:.4f}"
    )

    print(
        f"Precision: {precision:.4f}"
    )

    print(
        f"Recall   : {recall:.4f}"
    )

    print(
        f"F1 Score : {f1:.4f}"
    )

    print(
        f"ROC-AUC  : {roc_auc:.4f}"
    )

    print(
        "\nConfusion Matrix:"
    )

    print(cm)

    return {
        "model": name,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "roc_auc": roc_auc,
        "tn": cm[0, 0],
        "fp": cm[0, 1],
        "fn": cm[1, 0],
        "tp": cm[1, 1]
    }


# ============================================================
# EVALUATE
# ============================================================

results = []

results.append(
    evaluate_model(
        "HistGradientBoosting - Train",
        X_train,
        y_train
    )
)

results.append(
    evaluate_model(
        "HistGradientBoosting - Validation",
        X_val,
        y_val
    )
)

results.append(
    evaluate_model(
        "HistGradientBoosting - Test",
        X_test,
        y_test
    )
)


# ============================================================
# SAVE
# ============================================================

results_df = pd.DataFrame(
    results
)

results_df.to_csv(
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
    "=" * 60
)

print(
    OUTPUT_PATH
)

print(
    "\nExperiment completed successfully."
)