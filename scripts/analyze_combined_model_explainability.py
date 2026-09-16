import os
import numpy as np
import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
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

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "data",
    "ml"
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 60)
print("COMBINED MODEL EXPLAINABILITY ANALYSIS")
print("=" * 60)

train = pd.read_csv(TRAIN_PATH)
val = pd.read_csv(VAL_PATH)
test = pd.read_csv(TEST_PATH)

prediction = pd.read_csv(
    PREDICTION_FEATURE_PATH
)

prs = pd.read_csv(PR_PATH)

prs["pr_number"] = prs["pr_number"].astype(int)
prs["created_at"] = pd.to_datetime(
    prs["created_at"],
    utc=True
)


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

split_data = split_data[
    split_data["bottleneck_label"].notna()
].copy()

split_data = split_data.sort_values(
    "created_at"
).reset_index(drop=True)


total = len(split_data)

train_size = int(total * 0.70)
val_size = int(total * 0.15)

reconstructed_train = split_data.iloc[
    :train_size
]

reconstructed_val = split_data.iloc[
    train_size:
    train_size + val_size
]

reconstructed_test = split_data.iloc[
    train_size + val_size:
]


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
        "Temporal split mismatch."
    )

print("\n✓ Temporal split verified.")


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

embedding_lookup = {
    int(pr): embeddings[i]
    for i, pr in enumerate(
        embedding_map["pr_number"]
    )
}


def get_embeddings(pr_numbers):

    return np.asarray(
        [
            embedding_lookup[int(pr)]
            for pr in pr_numbers
        ],
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
].values

X_val_struct = val[
    structured_features
].values

X_test_struct = test[
    structured_features
].values


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
# SCALE STRUCTURED FEATURES
# ============================================================

scaler = StandardScaler()

X_train_struct_scaled = scaler.fit_transform(
    X_train_struct
)

X_val_struct_scaled = scaler.transform(
    X_val_struct
)

X_test_struct_scaled = scaler.transform(
    X_test_struct
)


# ============================================================
# COMBINE STRUCTURED + EMBEDDINGS
# ============================================================

X_train = np.hstack([
    X_train_struct_scaled,
    train_embeddings
])

X_val = np.hstack([
    X_val_struct_scaled,
    val_embeddings
])

X_test = np.hstack([
    X_test_struct_scaled,
    test_embeddings
])


print(
    "\nFeature dimensions:",
    X_train.shape
)


# ============================================================
# TRAIN CURRENT BEST MODEL
# ============================================================

print(
    "\nTraining Logistic Regression..."
)

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
    "✓ Model trained."
)


# ============================================================
# STRUCTURED FEATURE IMPORTANCE
# ============================================================

coefficients = model.coef_[0]

structured_coefficients = coefficients[
    :len(structured_features)
]

structured_explainability = pd.DataFrame({
    "feature": structured_features,
    "coefficient": structured_coefficients,
    "absolute_coefficient": np.abs(
        structured_coefficients
    )
})

structured_explainability = (
    structured_explainability
    .sort_values(
        "absolute_coefficient",
        ascending=False
    )
    .reset_index(drop=True)
)


# ============================================================
# INTERPRETATION
# ============================================================

structured_explainability[
    "direction"
] = np.where(
    structured_explainability[
        "coefficient"
    ] > 0,
    "increases_bottleneck_risk",
    "decreases_bottleneck_risk"
)


# ============================================================
# SAVE STRUCTURED EXPLANATIONS
# ============================================================

structured_output = os.path.join(
    OUTPUT_DIR,
    "combined_model_structured_explainability.csv"
)

structured_explainability.to_csv(
    structured_output,
    index=False
)


# ============================================================
# EMBEDDING COEFFICIENT SUMMARY
# ============================================================

embedding_coefficients = coefficients[
    len(structured_features):
]

embedding_summary = pd.DataFrame({
    "embedding_dimension": np.arange(
        1,
        len(embedding_coefficients) + 1
    ),
    "coefficient": embedding_coefficients,
    "absolute_coefficient": np.abs(
        embedding_coefficients
    )
})

embedding_summary = (
    embedding_summary
    .sort_values(
        "absolute_coefficient",
        ascending=False
    )
    .reset_index(drop=True)
)


embedding_output = os.path.join(
    OUTPUT_DIR,
    "combined_model_embedding_coefficients.csv"
)

embedding_summary.to_csv(
    embedding_output,
    index=False
)


# ============================================================
# PRINT RESULTS
# ============================================================

print(
    "\n" + "=" * 60
)

print(
    "STRUCTURED FEATURE IMPORTANCE"
)

print(
    "=" * 60
)

print(
    structured_explainability[
        [
            "feature",
            "coefficient",
            "direction"
        ]
    ].to_string(index=False)
)


print(
    "\n" + "=" * 60
)

print(
    "TOP POSITIVE STRUCTURED FEATURES"
)

print(
    "=" * 60
)

positive = structured_explainability[
    structured_explainability[
        "coefficient"
    ] > 0
]

print(
    positive[
        [
            "feature",
            "coefficient"
        ]
    ].head(10).to_string(index=False)
)


print(
    "\n" + "=" * 60
)

print(
    "TOP NEGATIVE STRUCTURED FEATURES"
)

print(
    "=" * 60
)

negative = structured_explainability[
    structured_explainability[
        "coefficient"
    ] < 0
]

print(
    negative[
        [
            "feature",
            "coefficient"
        ]
    ].head(10).to_string(index=False)
)


print(
    "\n" + "=" * 60
)

print(
    "FILES SAVED"
)

print(
    structured_output
)

print(
    embedding_output
)

print(
    "\nExplainability analysis completed."
)