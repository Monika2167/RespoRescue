import os
import joblib
import numpy as np
import pandas as pd


# ============================================================
# REPORESCUE - REUSABLE PR PREDICTION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)


# ============================================================
# PATHS
# ============================================================

MODEL_DIR = os.path.join(
    BASE_DIR,
    "data",
    "ml",
    "model_artifacts"
)

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

CONFIG_PATH = os.path.join(
    MODEL_DIR,
    "model_config.joblib"
)

PREDICTION_FEATURE_PATH = os.path.join(
    BASE_DIR,
    "data",
    "features",
    "pr_24h_prediction_features.csv"
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


# ============================================================
# LOAD MODEL ARTIFACTS
# ============================================================

print("Loading RepoRescue ML model...")

model = joblib.load(
    MODEL_PATH
)

scaler = joblib.load(
    SCALER_PATH
)

structured_features = joblib.load(
    FEATURES_PATH
)

config = joblib.load(
    CONFIG_PATH
)

threshold = config[
    "threshold"
]


# ============================================================
# LOAD PREDICTION DATA
# ============================================================

prediction_features = pd.read_csv(
    PREDICTION_FEATURE_PATH
)

prediction_features[
    "pr_number"
] = prediction_features[
    "pr_number"
].astype(int)


# ============================================================
# LOAD EMBEDDINGS
# ============================================================

embeddings = np.load(
    EMBEDDING_PATH
)

embedding_map = pd.read_csv(
    EMBEDDING_MAP_PATH
)

embedding_map[
    "pr_number"
] = embedding_map[
    "pr_number"
].astype(int)


embedding_lookup = {
    int(pr): embeddings[i]
    for i, pr in enumerate(
        embedding_map["pr_number"]
    )
}


# ============================================================
# FEATURE NAME MAPPING
# ============================================================

FEATURE_NAMES = {

    "title_length":
        "Title length",

    "body_length":
        "Description length",

    "title_word_count":
        "Number of title words",

    "body_word_count":
        "Number of description words",

    "is_draft":
        "Draft status",

    "commits_24h":
        "Commits in first 24 hours",

    "commit_authors_24h":
        "Contributing developers in first 24 hours",

    "files_changed_24h":
        "Files changed in first 24 hours",

    "additions_24h":
        "Lines added in first 24 hours",

    "deletions_24h":
        "Lines deleted in first 24 hours",

    "total_changes_24h":
        "Total code changes in first 24 hours",

    "changes_per_commit_24h":
        "Changes per commit",

    "files_per_commit_24h":
        "Files per commit",

    "deletion_ratio_24h":
        "Deletion ratio",

    "has_commit_activity_24h":
        "Commit activity during first 24 hours",

    "has_file_activity_24h":
        "File activity during first 24 hours"
}


# ============================================================
# PREDICTION FUNCTION
# ============================================================

def predict_pr(pr_number):

    """
    Predict whether a PR is a potential
    future maintenance bottleneck.

    Returns a dictionary containing:
    - PR number
    - probability
    - prediction
    - threshold
    - top model evidence
    - semantic signal
    """


    # --------------------------------------------------------
    # Find PR
    # --------------------------------------------------------

    pr_data = prediction_features[
        prediction_features[
            "pr_number"
        ] == int(pr_number)
    ]


    if pr_data.empty:

        return {
            "success": False,
            "error":
                "No 24-hour prediction data available "
                f"for PR #{pr_number}."
        }


    row = pr_data.iloc[0]


    # --------------------------------------------------------
    # Check embedding
    # --------------------------------------------------------

    if int(pr_number) not in embedding_lookup:

        return {
            "success": False,
            "error":
                "Embedding not found "
                f"for PR #{pr_number}."
        }


    # --------------------------------------------------------
    # Structured features
    # --------------------------------------------------------

    structured = row[
        structured_features
    ].values.astype(
        float
    ).reshape(
        1, -1
    )


    structured_scaled = (
        scaler.transform(
            structured
        )
    )


    # --------------------------------------------------------
    # Semantic embedding
    # --------------------------------------------------------

    embedding = embedding_lookup[
        int(pr_number)
    ].reshape(
        1, -1
    )


    # --------------------------------------------------------
    # Combine
    # --------------------------------------------------------

    X = np.hstack([
        structured_scaled,
        embedding
    ])


    # --------------------------------------------------------
    # Probability
    # --------------------------------------------------------

    probability = model.predict_proba(
        X
    )[0, 1]


    # --------------------------------------------------------
    # Classification
    # --------------------------------------------------------

    prediction = int(
        probability >= threshold
    )


    if prediction == 1:

        label = (
            "Potential Bottleneck"
        )

    else:

        label = (
            "Lower Bottleneck Risk"
        )


    # ========================================================
    # STRUCTURED FEATURE CONTRIBUTIONS
    # ========================================================

    coefficients = model.coef_[0]

    structured_coefficients = (
        coefficients[
            :len(structured_features)
        ]
    )


    contributions = []


    for i, feature in enumerate(
        structured_features
    ):

        contribution = (
            structured_scaled[0, i]
            *
            structured_coefficients[i]
        )


        contributions.append({

            "feature":
                feature,

            "feature_name":
                FEATURE_NAMES.get(
                    feature,
                    feature
                ),

            "value":
                float(row[feature]),

            "coefficient":
                float(
                    structured_coefficients[i]
                ),

            "contribution":
                float(
                    contribution
                )

        })


    contributions = sorted(
        contributions,
        key=lambda x:
            abs(x["contribution"]),
        reverse=True
    )


    # --------------------------------------------------------
    # Top 6 evidence
    # --------------------------------------------------------

    top_evidence = []


    for item in contributions:

        contribution = (
            item["contribution"]
        )

        if abs(contribution) < 0.03:

            continue


        feature = item[
            "feature"
        ]

        value = item[
            "value"
        ]


        # ----------------------------------------------------
        # Binary features
        # ----------------------------------------------------

        if feature == "is_draft":

            if value == 1:

                description = (
                    "PR is marked as a draft"
                )

            else:

                description = (
                    "PR is not marked as a draft"
                )


        elif feature == "has_commit_activity_24h":

            if value == 1:

                description = (
                    "Commit activity was observed "
                    "during the first 24 hours"
                )

            else:

                description = (
                    "No commit activity was observed "
                    "during the first 24 hours"
                )


        elif feature == "has_file_activity_24h":

            if value == 1:

                description = (
                    "File activity was observed "
                    "during the first 24 hours"
                )

            else:

                description = (
                    "No file activity was observed "
                    "during the first 24 hours"
                )


        # ----------------------------------------------------
        # Numerical features
        # ----------------------------------------------------

        else:

            if feature == (
                "deletion_ratio_24h"
            ):

                value_text = (
                    f"{value:.2%}"
                )

            elif float(value).is_integer():

                value_text = (
                    f"{int(value)}"
                )

            else:

                value_text = (
                    f"{value:.2f}"
                )


            description = (
                f"{FEATURE_NAMES.get(feature, feature)} "
                f"= {value_text}"
            )


        # ----------------------------------------------------
        # Direction
        # ----------------------------------------------------

        if contribution > 0:

            direction = "higher"

        else:

            direction = "lower"


        top_evidence.append({

            "feature":
                feature,

            "description":
                description,

            "contribution":
                round(
                    float(contribution),
                    6
                ),

            "direction":
                direction,

            "explanation":
                (
                    f"{description}; "
                    f"this feature pushed the model "
                    f"toward {direction} bottleneck risk."
                )

        })


        if len(top_evidence) >= 6:

            break


    # ========================================================
    # SEMANTIC SIGNAL
    # ========================================================

    embedding_start = len(
        structured_features
    )


    embedding_contributions = (
        coefficients[
            embedding_start:
        ]
        *
        embedding[0]
    )


    semantic_strength = float(
        np.sum(
            embedding_contributions
        )
    )


    if semantic_strength > 0:

        semantic_signal = "positive"

    else:

        semantic_signal = "negative"


    # ========================================================
    # FINAL RESULT
    # ========================================================

    return {

        "success":
            True,

        "pr_number":
            int(pr_number),

        "probability":
            round(
                float(probability),
                6
            ),

        "probability_percent":
            round(
                float(probability * 100),
                2
            ),

        "prediction":
            label,

        "threshold":
            threshold,

        "top_evidence":
            top_evidence,

        "semantic_signal":
            semantic_signal,

        "semantic_strength":
            round(
                semantic_strength,
                6
            )

    }


# ============================================================
# SIMPLE TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("REPORESCUE ML PREDICTION MODULE")
    print("=" * 60)

    print(
        f"\n✓ Decision threshold: {threshold}"
    )

    print(
        f"✓ Structured features: "
        f"{len(structured_features)}"
    )

    print(
        f"✓ Semantic embedding dimensions: "
        f"{embeddings.shape[1]}"
    )

    print(
        "\n✓ Module is ready for FastAPI integration."
    )

    print("=" * 60)