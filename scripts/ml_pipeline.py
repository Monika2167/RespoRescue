import os
import joblib
import numpy as np
import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler


# ============================================================
# REPORESCUE ML PIPELINE
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)


# ============================================================
# PATHS
# ============================================================

TRAIN_PATH = os.path.join(
    BASE_DIR,
    "data",
    "ml",
    "train.csv"
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

MODEL_DIR = os.path.join(
    BASE_DIR,
    "data",
    "ml",
    "model_artifacts"
)


os.makedirs(
    MODEL_DIR,
    exist_ok=True
)


# ============================================================
# CONFIGURATION
# ============================================================

THRESHOLD = 0.57


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


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 60)
print("REPORESCUE ML PIPELINE")
print("=" * 60)

print("\nLoading datasets...")

train = pd.read_csv(
    TRAIN_PATH
)

prediction_features = pd.read_csv(
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

print(
    f"✓ Training rows: {len(train):,}"
)

print(
    f"✓ Prediction rows: "
    f"{len(prediction_features):,}"
)


# ============================================================
# LOAD EMBEDDINGS
# ============================================================

print("\nLoading embeddings...")

embeddings = np.load(
    EMBEDDING_PATH
)

embedding_map = pd.read_csv(
    EMBEDDING_MAP_PATH
)

embedding_map["pr_number"] = (
    embedding_map["pr_number"].astype(int)
)


embedding_lookup = {
    int(pr): embeddings[i]
    for i, pr in enumerate(
        embedding_map["pr_number"]
    )
}

print(
    f"✓ Embeddings loaded: "
    f"{len(embedding_lookup):,}"
)


# ============================================================
# RECONSTRUCT TEMPORAL TRAINING PRs
# ============================================================

print("\nReconstructing training PR mapping...")

split_data = prediction_features[
    [
        "pr_number",
        "bottleneck_label"
    ]
].copy()


split_data = split_data[
    split_data["bottleneck_label"].notna()
].copy()


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


split_data = split_data.sort_values(
    "created_at"
).reset_index(drop=True)


train_size = len(train)


train_pr_numbers = (
    split_data.iloc[:train_size][
        "pr_number"
    ]
    .astype(int)
    .values
)


print(
    f"✓ Training PRs mapped: "
    f"{len(train_pr_numbers):,}"
)


# ============================================================
# PREPARE STRUCTURED TRAINING FEATURES
# ============================================================

print("\nPreparing structured features...")

X_train_struct = train[
    STRUCTURED_FEATURES
].values.astype(float)


y_train = train[
    "bottleneck_label"
].astype(int).values


# ============================================================
# SCALE STRUCTURED FEATURES
# ============================================================

print("Scaling structured features...")

scaler = StandardScaler()


X_train_struct_scaled = (
    scaler.fit_transform(
        X_train_struct
    )
)


# ============================================================
# PREPARE TRAINING EMBEDDINGS
# ============================================================

print("Preparing semantic embeddings...")

train_embeddings = np.asarray(
    [
        embedding_lookup[int(pr)]
        for pr in train_pr_numbers
    ],
    dtype=np.float32
)


# ============================================================
# COMBINE STRUCTURED + SEMANTIC FEATURES
# ============================================================

print("Combining structured + semantic features...")

X_train = np.hstack([
    X_train_struct_scaled,
    train_embeddings
])


print(
    f"✓ Final training shape: "
    f"{X_train.shape}"
)


# ============================================================
# TRAIN LOGISTIC REGRESSION
# ============================================================

print("\nTraining Logistic Regression model...")

model = LogisticRegression(
    max_iter=3000,
    class_weight="balanced",
    random_state=42
)


model.fit(
    X_train,
    y_train
)


print("✓ Model trained successfully.")


# ============================================================
# SAVE MODEL
# ============================================================

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "combined_logistic_regression.joblib"
)

SCALER_PATH = os.path.join(
    MODEL_DIR,
    "structured_scaler.joblib"
)

FEATURES_PATH = os.path.join(
    MODEL_DIR,
    "model_features.joblib"
)


joblib.dump(
    model,
    MODEL_PATH
)

joblib.dump(
    scaler,
    SCALER_PATH
)

joblib.dump(
    STRUCTURED_FEATURES,
    FEATURES_PATH
)


# ============================================================
# SAVE MODEL CONFIGURATION
# ============================================================

config = {
    "model_type":
        "Scaled Combined Logistic Regression",

    "threshold":
        THRESHOLD,

    "structured_features":
        STRUCTURED_FEATURES,

    "embedding_dimensions":
        int(embeddings.shape[1]),

    "training_rows":
        int(len(train)),

    "class_weight":
        "balanced",

    "max_iter":
        3000,

    "random_state":
        42
}


CONFIG_PATH = os.path.join(
    MODEL_DIR,
    "model_config.joblib"
)


joblib.dump(
    config,
    CONFIG_PATH
)


# ============================================================
# COMPLETION MESSAGE
# ============================================================

print("\n" + "=" * 60)

print(
    "MODEL ARTIFACTS SAVED SUCCESSFULLY"
)

print("=" * 60)

print(
    f"\nModel  : {MODEL_PATH}"
)

print(
    f"Scaler : {SCALER_PATH}"
)

print(
    f"Config : {CONFIG_PATH}"
)

print(
    f"Features: {FEATURES_PATH}"
)

print(
    f"\nDecision threshold: {THRESHOLD}"
)

print(
    "\n✓ RepoRescue ML pipeline is ready "
    "for backend integration."
)

print("=" * 60)