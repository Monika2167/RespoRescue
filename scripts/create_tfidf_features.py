import os
import pandas as pd
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FEATURE_PATH = os.path.join(
    BASE_DIR, "data", "features", "pr_24h_prediction_features.csv"
)

PR_PATH = os.path.join(
    BASE_DIR, "data", "preprocessed", "pull_requests_preprocessed.csv"
)

ML_DIR = os.path.join(BASE_DIR, "data", "ml")

OUTPUT_DIR = os.path.join(BASE_DIR, "data", "nlp")
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 60)
print("REPORESCUE - TF-IDF NLP FEATURE ENGINEERING")
print("=" * 60)

features = pd.read_csv(FEATURE_PATH)
prs = pd.read_csv(PR_PATH)

print(f"Prediction feature rows : {len(features)}")
print(f"PR rows                 : {len(prs)}")


# ============================================================
# PREPARE PR TEXT
# ============================================================

prs["title"] = prs["title"].fillna("").astype(str)
prs["body"] = prs["body"].fillna("").astype(str)

prs["text"] = (
    prs["title"].str.strip()
    + " "
    + prs["body"].str.strip()
)

# Keep only PRs present in our labeled prediction dataset
text_data = features[["pr_number"]].merge(
    prs[["pr_number", "text"]],
    on="pr_number",
    how="left"
)

text_data["text"] = text_data["text"].fillna("")

print(f"Text records prepared : {len(text_data)}")


# ============================================================
# GET TEMPORAL SPLIT PR NUMBERS
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

# Recover PR numbers using the original prediction feature file
split_info = features[["pr_number"]].copy()

# The ML datasets have the same row order as the temporal split
split_info["split"] = ""

split_info.loc[:len(train) - 1, "split"] = "train"

split_info.loc[
    len(train):len(train) + len(validation) - 1,
    "split"
] = "validation"

split_info.loc[
    len(train) + len(validation):,
    "split"
] = "test"


# ============================================================
# MERGE SPLIT INFORMATION WITH TEXT
# ============================================================

text_data = text_data.merge(
    split_info,
    on="pr_number",
    how="left"
)

print("\nTemporal split:")
print(text_data["split"].value_counts())


# ============================================================
# TF-IDF
# ============================================================

print("\nTraining TF-IDF vocabulary...")

vectorizer = TfidfVectorizer(
    lowercase=True,
    stop_words="english",
    ngram_range=(1, 2),
    min_df=3,
    max_df=0.95,
    sublinear_tf=True,
    max_features=20000
)

train_text = text_data.loc[
    text_data["split"] == "train",
    "text"
]

validation_text = text_data.loc[
    text_data["split"] == "validation",
    "text"
]

test_text = text_data.loc[
    text_data["split"] == "test",
    "text"
]


# IMPORTANT:
# Fit ONLY on training text
X_train = vectorizer.fit_transform(train_text)

# Transform validation/test using training vocabulary
X_validation = vectorizer.transform(validation_text)

X_test = vectorizer.transform(test_text)


# ============================================================
# DISPLAY INFORMATION
# ============================================================

print("\nTF-IDF completed.")

print(f"Training samples    : {X_train.shape[0]}")
print(f"Validation samples  : {X_validation.shape[0]}")
print(f"Test samples        : {X_test.shape[0]}")
print(f"TF-IDF features     : {X_train.shape[1]}")


# ============================================================
# SAVE SPARSE MATRICES
# ============================================================

from scipy.sparse import save_npz

save_npz(
    os.path.join(OUTPUT_DIR, "tfidf_train.npz"),
    X_train
)

save_npz(
    os.path.join(OUTPUT_DIR, "tfidf_validation.npz"),
    X_validation
)

save_npz(
    os.path.join(OUTPUT_DIR, "tfidf_test.npz"),
    X_test
)


# ============================================================
# SAVE VOCABULARY
# ============================================================

vocabulary = pd.DataFrame(
    {
        "term": vectorizer.get_feature_names_out()
    }
)

vocabulary.to_csv(
    os.path.join(OUTPUT_DIR, "tfidf_vocabulary.csv"),
    index=False
)


# ============================================================
# SAVE PR MAPPING
# ============================================================

for split_name in ["train", "validation", "test"]:

    split_prs = text_data[
        text_data["split"] == split_name
    ][["pr_number"]]

    split_prs.to_csv(
        os.path.join(
            OUTPUT_DIR,
            f"{split_name}_pr_numbers.csv"
        ),
        index=False
    )


print("\nSaved to:")
print(OUTPUT_DIR)

print("\n" + "=" * 60)
print("TF-IDF NLP STEP COMPLETED")
print("=" * 60)