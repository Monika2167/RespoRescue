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
# HUMAN-READABLE FEATURE NAMES
# ============================================================

FEATURE_NAMES = {

    "title_length":
        "title length",

    "body_length":
        "description length",

    "title_word_count":
        "number of title words",

    "body_word_count":
        "number of description words",

    "is_draft":
        "draft status",

    "commits_24h":
        "commits in first 24 hours",

    "commit_authors_24h":
        "developers contributing in first 24 hours",

    "files_changed_24h":
        "files changed in first 24 hours",

    "additions_24h":
        "lines added in first 24 hours",

    "deletions_24h":
        "lines deleted in first 24 hours",

    "total_changes_24h":
        "total code changes in first 24 hours",

    "changes_per_commit_24h":
        "changes per commit",

    "files_per_commit_24h":
        "files per commit",

    "deletion_ratio_24h":
        "deletion ratio",

    "has_commit_activity_24h":
        "commit activity during first 24 hours",

    "has_file_activity_24h":
        "file activity during first 24 hours"
}


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 60)
print("REPORESCUE - PR PREDICTION & EXPLANATION")
print("=" * 60)

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


# ============================================================
# RECONSTRUCT TRAINING PR NUMBERS
# ============================================================

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
    ].astype(int).values
)


# ============================================================
# TRAINING DATA
# ============================================================

X_train_struct = train[
    STRUCTURED_FEATURES
].values.astype(float)

y_train = train[
    "bottleneck_label"
].astype(int).values


# ============================================================
# SCALE STRUCTURED FEATURES
# ============================================================

scaler = StandardScaler()

X_train_struct_scaled = (
    scaler.fit_transform(
        X_train_struct
    )
)


# ============================================================
# TRAIN EMBEDDINGS
# ============================================================

train_embeddings = np.asarray(
    [
        embedding_lookup[int(pr)]
        for pr in train_pr_numbers
    ],
    dtype=np.float32
)


# ============================================================
# COMBINE FEATURES
# ============================================================

X_train = np.hstack([
    X_train_struct_scaled,
    train_embeddings
])


# ============================================================
# TRAIN MODEL
# ============================================================

print("\nTraining prediction model...")

model = LogisticRegression(
    max_iter=3000,
    class_weight="balanced",
    random_state=42
)

model.fit(
    X_train,
    y_train
)

print("✓ Model ready.")


# ============================================================
# MODEL COEFFICIENTS
# ============================================================

coefficients = model.coef_[0]

structured_coefficients = (
    coefficients[
        :len(STRUCTURED_FEATURES)
    ]
)


# ============================================================
# DISPLAY AVAILABLE PR COUNT
# ============================================================

available_prs = (
    prediction_features[
        "pr_number"
    ]
    .dropna()
    .astype(int)
    .unique()
)

print(
    f"\nPrediction data available for "
    f"{len(available_prs):,} PRs."
)


# ============================================================
# USER INPUT LOOP
# ============================================================

while True:

    user_input = input(
        "\nEnter PR number "
        "(or type 'exit'): "
    ).strip()


    if user_input.lower() == "exit":

        print(
            "\nExiting RepoRescue."
        )

        break


    try:

        pr_number = int(
            user_input
        )

    except ValueError:

        print(
            "❌ Please enter a valid PR number."
        )

        continue


    # ========================================================
    # FIND PREDICTION DATA
    # ========================================================

    pr_data = prediction_features[
        prediction_features[
            "pr_number"
        ] == pr_number
    ]


    if pr_data.empty:

        print(
            f"\n❌ No 24-hour prediction data "
            f"is available for PR #{pr_number}."
        )

        print(
            "This PR may not contain enough "
            "information for the current prediction dataset."
        )

        continue


    row = pr_data.iloc[0]


    # ========================================================
    # GET STRUCTURED FEATURES
    # ========================================================

    structured = row[
        STRUCTURED_FEATURES
    ].values.astype(float).reshape(
        1, -1
    )

    structured_scaled = (
        scaler.transform(
            structured
        )
    )


    # ========================================================
    # GET EMBEDDING
    # ========================================================

    if pr_number not in embedding_lookup:

        print(
            f"\n❌ Embedding not found "
            f"for PR #{pr_number}."
        )

        continue


    embedding = embedding_lookup[
        pr_number
    ].reshape(1, -1)


    # ========================================================
    # FINAL INPUT
    # ========================================================

    X_pr = np.hstack([
        structured_scaled,
        embedding
    ])


    # ========================================================
    # PREDICTION
    # ========================================================

    probability = model.predict_proba(
        X_pr
    )[0, 1]

    prediction = int(
        probability >= THRESHOLD
    )


    # ========================================================
    # PR DETAILS
    # ========================================================

    pr_info = prs[
        prs["pr_number"] == pr_number
    ]


    if not pr_info.empty:

        pr_row = pr_info.iloc[0]

        title = str(
            pr_row.get(
                "title",
                "Unknown"
            )
        )

        author = str(
            pr_row.get(
                "author",
                "Unknown"
            )
        )

    else:

        title = "Unknown"
        author = "Unknown"


    # ========================================================
    # HEADER
    # ========================================================

    print(
        "\n" + "=" * 60
    )

    print(
        f"PR #{pr_number}"
    )

    print(
        f"Title : {title}"
    )

    print(
        f"Author: {author}"
    )

    print(
        "=" * 60
    )

    print(
        f"\nBottleneck probability: "
        f"{probability:.2%}"
    )

    print(
        f"Decision threshold: "
        f"{THRESHOLD:.2f}"
    )


    if prediction == 1:

        print(
            "\n⚠️ PREDICTED: "
            "Potential Bottleneck"
        )

    else:

        print(
            "\n✅ PREDICTED: "
            "Lower Bottleneck Risk"
        )


    # ========================================================
    # LOCAL FEATURE CONTRIBUTIONS
    # ========================================================

    contributions = []

    for i, feature in enumerate(
        STRUCTURED_FEATURES
    ):

        scaled_value = (
            structured_scaled[0, i]
        )

        coefficient = (
            structured_coefficients[i]
        )

        contribution = (
            scaled_value *
            coefficient
        )

        contributions.append({

            "feature": feature,

            "value":
                float(row[feature]),

            "scaled_value":
                float(scaled_value),

            "coefficient":
                float(coefficient),

            "contribution":
                float(contribution)

        })


    contributions_df = pd.DataFrame(
        contributions
    )

    contributions_df[
        "absolute_contribution"
    ] = np.abs(
        contributions_df[
            "contribution"
        ]
    )


    contributions_df = (
        contributions_df
        .sort_values(
            "absolute_contribution",
            ascending=False
        )
        .reset_index(drop=True)
    )


    # ========================================================
    # TOP MODEL EVIDENCE
    # ========================================================

    print(
        "\n" + "-" * 60
    )

    print(
        "TOP MODEL EVIDENCE"
    )

    print(
        "-" * 60
    )


    displayed = 0


    for _, item in (
        contributions_df.iterrows()
    ):

        feature = item[
            "feature"
        ]

        value = item[
            "value"
        ]

        contribution = item[
            "contribution"
        ]


        if abs(contribution) < 0.03:

            continue


        name = FEATURE_NAMES[
            feature
        ]


        # ====================================================
        # BINARY FEATURES
        # ====================================================

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


        # ====================================================
        # NUMERICAL FEATURES
        # ====================================================

        else:

            if feature == "deletion_ratio_24h":

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
                f"{name.capitalize()} = "
                f"{value_text}"
            )


        # ====================================================
        # CONTRIBUTION DIRECTION
        # ====================================================

        if contribution > 0:

            print(
                f"• ↑ {description}; "
                "model contribution increased "
                "the bottleneck score."
            )

        else:

            print(
                f"• ↓ {description}; "
                "model contribution decreased "
                "the bottleneck score."
            )


        displayed += 1


        if displayed >= 6:

            break


    # ========================================================
    # SEMANTIC SIGNAL
    # ========================================================

    embedding_start = len(
        STRUCTURED_FEATURES
    )

    embedding_contributions = (
        coefficients[
            embedding_start:
        ] *
        embedding[0]
    )

    semantic_strength = np.sum(
        embedding_contributions
    )


    print(
        "\n" + "-" * 60
    )

    print(
        "SEMANTIC MODEL SIGNAL"
    )

    print(
        "-" * 60
    )


    if semantic_strength > 0:

        print(
            "• PR text contributed a positive "
            "semantic signal toward the bottleneck score."
        )

    else:

        print(
            "• PR text contributed a negative "
            "semantic signal toward the bottleneck score."
        )


    # ========================================================
    # FINAL INTERPRETATION
    # ========================================================

    print(
        "\n" + "-" * 60
    )

    print(
        "REPORESCUE INTERPRETATION"
    )

    print(
        "-" * 60
    )


    if prediction == 1:

        print(
            "RepoRescue identifies this PR as "
            "a potential future maintenance bottleneck."
        )

        print(
            "This prediction combines structured "
            "early-activity features with semantic "
            "information from the PR text."
        )

    else:

        print(
            "RepoRescue does not classify this PR "
            "as a potential bottleneck at the "
            "current decision threshold."
        )

        print(
            "This prediction is not a guarantee "
            "of fast resolution."
        )


    # ========================================================
    # SAVE EXPLANATION
    # ========================================================

    explanation_path = os.path.join(
        OUTPUT_DIR,
        f"explanation_pr_{pr_number}.csv"
    )

    contributions_df.to_csv(
        explanation_path,
        index=False
    )

    print(
        "\nExplanation saved:"
    )

    print(
        explanation_path
    )