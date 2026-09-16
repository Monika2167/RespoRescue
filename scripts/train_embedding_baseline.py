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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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

PREDICTION_FEATURES_PATH = os.path.join(
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

# ============================================================
# LOAD DATA
# ============================================================

print("=" * 60)
print("SEMANTIC EMBEDDING BASELINE")
print("=" * 60)

print("\nLoading embeddings...")

X_embeddings = np.load(EMBEDDING_PATH)

embedding_ids = pd.read_csv(EMBEDDING_IDS_PATH)

features = pd.read_csv(PREDICTION_FEATURES_PATH)

pr_clean = pd.read_csv(PR_CLEAN_PATH)

print("Embedding shape:", X_embeddings.shape)
print("Embedding IDs:", len(embedding_ids))
print("Prediction rows:", len(features))

# ============================================================
# PREPARE PR METADATA
# ============================================================

pr_clean["created_at"] = pd.to_datetime(
    pr_clean["created_at"],
    utc=True
)

# Keep only PRs present in the prediction dataset
metadata = pr_clean[
    ["pr_number", "created_at"]
].copy()

# Merge creation time with prediction data
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

# ============================================================
# VERIFY EXPECTED SPLIT
# ============================================================

TRAIN_SIZE = 3393
VAL_SIZE = 727
TEST_SIZE = 728

expected_total = TRAIN_SIZE + VAL_SIZE + TEST_SIZE

if len(data) != expected_total:
    raise ValueError(
        f"Expected {expected_total} rows, "
        f"but found {len(data)} rows."
    )

# ============================================================
# CREATE TEMPORAL SPLITS
# ============================================================

train_data = data.iloc[:TRAIN_SIZE].copy()

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
# MAP PR NUMBER → EMBEDDING
# ============================================================

embedding_ids["pr_number"] = embedding_ids["pr_number"].astype(int)

embedding_map = {
    pr_number: index
    for index, pr_number
    in enumerate(embedding_ids["pr_number"])
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

    return X_embeddings[indices]


X_train = get_embeddings(train_data)
X_val = get_embeddings(val_data)
X_test = get_embeddings(test_data)

y_train = train_data["bottleneck_label"].astype(int).values
y_val = val_data["bottleneck_label"].astype(int).values
y_test = test_data["bottleneck_label"].astype(int).values

# ============================================================
# VERIFY SHAPES
# ============================================================

print("\nEmbedding split shapes:")
print("X_train:", X_train.shape)
print("X_val  :", X_val.shape)
print("X_test :", X_test.shape)

print("\nTarget distribution:")

print(
    "Train:",
    dict(zip(*np.unique(y_train, return_counts=True)))
)

print(
    "Validation:",
    dict(zip(*np.unique(y_val, return_counts=True)))
)

print(
    "Test:",
    dict(zip(*np.unique(y_test, return_counts=True)))
)

# ============================================================
# TRAIN LOGISTIC REGRESSION
# ============================================================

print("\nTraining Logistic Regression...")

model = LogisticRegression(
    max_iter=2000,
    class_weight="balanced",
    random_state=42
)

model.fit(
    X_train,
    y_train
)

print("Training complete.")

# ============================================================
# EVALUATION FUNCTION
# ============================================================

def evaluate_model(name, X, y):

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
    print(name)
    print("=" * 60)

    print(f"Accuracy  : {accuracy:.4f}")
    print(f"Precision : {precision:.4f}")
    print(f"Recall    : {recall:.4f}")
    print(f"F1 Score  : {f1:.4f}")
    print(f"ROC-AUC   : {roc_auc:.4f}")

    print("\nConfusion Matrix:")
    print(cm)

    return {
        "dataset": name,
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

val_results = evaluate_model(
    "VALIDATION",
    X_val,
    y_val
)

test_results = evaluate_model(
    "TEST",
    X_test,
    y_test
)

# ============================================================
# SAVE RESULTS
# ============================================================

results = pd.DataFrame([
    train_results,
    val_results,
    test_results
])

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "data",
    "ml"
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

results_path = os.path.join(
    OUTPUT_DIR,
    "embedding_baseline_results.csv"
)

results.to_csv(
    results_path,
    index=False
)

print("\nResults saved to:")
print(results_path)

print("\n" + "=" * 60)
print("SEMANTIC EMBEDDING BASELINE FINISHED")
print("=" * 60)