import pandas as pd
from pathlib import Path

# ============================================
# REPORESCUE - TEMPORAL ML SPLIT
# ============================================

BASE_DIR = Path(__file__).resolve().parent.parent

FEATURE_FILE = (
    BASE_DIR
    / "data"
    / "features"
    / "pr_24h_prediction_features.csv"
)

ML_FILE = (
    BASE_DIR
    / "data"
    / "ml"
    / "bottleneck_ml_dataset.csv"
)

OUTPUT_DIR = (
    BASE_DIR
    / "data"
    / "ml"
)

TRAIN_FILE = OUTPUT_DIR / "train.csv"
VAL_FILE = OUTPUT_DIR / "validation.csv"
TEST_FILE = OUTPUT_DIR / "test.csv"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

print("=" * 60)
print("REPORESCUE - TEMPORAL ML SPLIT")
print("=" * 60)

# ============================================
# 1. LOAD DATA
# ============================================

print("\nLoading datasets...")

features = pd.read_csv(FEATURE_FILE)
ml_df = pd.read_csv(ML_FILE)

print(
    f"24-hour feature rows : {len(features)}"
)

print(
    f"ML dataset rows      : {len(ml_df)}"
)

# ============================================
# 2. GET PR CREATION TIMES
# ============================================
# The ML dataset intentionally does not contain
# pr_number because it is an identifier.
#
# We retrieve the PR number + creation time from
# the original 24-hour feature dataset.

metadata = features[
    ["pr_number"]
].copy()

# We need creation time from the original
# preprocessed PR dataset.

PR_FILE = (
    BASE_DIR
    / "data"
    / "preprocessed"
    / "pull_requests_preprocessed.csv"
)

prs = pd.read_csv(
    PR_FILE,
    usecols=[
        "pr_number",
        "created_at"
    ]
)

prs["created_at"] = pd.to_datetime(
    prs["created_at"],
    utc=True,
    errors="coerce"
)

# ============================================
# 3. CONNECT PR NUMBER TO ML DATA
# ============================================

metadata = metadata.merge(
    prs,
    on="pr_number",
    how="left",
    validate="one_to_one"
)

# Make sure PR numbers in the feature dataset
# are unique.

if metadata["pr_number"].duplicated().any():

    raise ValueError(
        "Duplicate PR numbers found in metadata."
    )

# ============================================
# 4. CHECK ML DATA ALIGNMENT
# ============================================

if len(metadata) != len(features):

    raise ValueError(
        "Feature metadata row count mismatch."
    )

# Match target from the feature dataset
# to PR number.

metadata["bottleneck_label"] = (
    features["bottleneck_label"].values
)

# ============================================
# 5. CREATE ORDERING DATA
# ============================================

metadata = metadata.sort_values(
    "created_at"
).reset_index(drop=True)

# ============================================
# 6. CHECK TARGET VALUES
# ============================================

if metadata["bottleneck_label"].isna().any():

    raise ValueError(
        "Missing bottleneck labels found."
    )

# ============================================
# 7. TEMPORAL SPLIT
# ============================================
#
# 70% -> Training
# 15% -> Validation
# 15% -> Test

total = len(metadata)

train_end = int(total * 0.70)

validation_end = int(total * 0.85)

train_meta = metadata.iloc[
    :train_end
].copy()

validation_meta = metadata.iloc[
    train_end:validation_end
].copy()

test_meta = metadata.iloc[
    validation_end:
].copy()

# ============================================
# 8. GET PR NUMBERS FOR EACH SPLIT
# ============================================

train_prs = set(
    train_meta["pr_number"]
)

validation_prs = set(
    validation_meta["pr_number"]
)

test_prs = set(
    test_meta["pr_number"]
)

# ============================================
# 9. BUILD FINAL SPLIT DATASETS
# ============================================
#
# Use the already-prepared ML dataset.
#
# We recover the PR number only temporarily
# to identify which rows belong to each split.

ml_with_id = features[
    ["pr_number"]
].copy()

ml_with_id = pd.concat(
    [
        ml_with_id.reset_index(drop=True),
        ml_df.reset_index(drop=True)
    ],
    axis=1
)

# ============================================
# 10. CREATE SPLITS
# ============================================

train = ml_with_id[
    ml_with_id["pr_number"].isin(
        train_prs
    )
].copy()

validation = ml_with_id[
    ml_with_id["pr_number"].isin(
        validation_prs
    )
].copy()

test = ml_with_id[
    ml_with_id["pr_number"].isin(
        test_prs
    )
].copy()

# ============================================
# 11. SORT EACH SPLIT
# ============================================

date_lookup = metadata[
    ["pr_number", "created_at"]
]

train = train.merge(
    date_lookup,
    on="pr_number",
    how="left",
    validate="one_to_one"
)

validation = validation.merge(
    date_lookup,
    on="pr_number",
    how="left",
    validate="one_to_one"
)

test = test.merge(
    date_lookup,
    on="pr_number",
    how="left",
    validate="one_to_one"
)

train = train.sort_values(
    "created_at"
)

validation = validation.sort_values(
    "created_at"
)

test = test.sort_values(
    "created_at"
)

# ============================================
# 12. DISPLAY SPLIT INFORMATION
# ============================================

print("\n" + "=" * 60)
print("TEMPORAL SPLIT SUMMARY")
print("=" * 60)

print(
    f"\nTotal rows      : {total}"
)

print(
    f"Train rows      : {len(train)}"
)

print(
    f"Validation rows : {len(validation)}"
)

print(
    f"Test rows       : {len(test)}"
)

# ============================================
# 13. DATE RANGES
# ============================================

def print_range(name, data):

    print(f"\n{name}")

    print(
        f"Start: "
        f"{data['created_at'].min()}"
    )

    print(
        f"End  : "
        f"{data['created_at'].max()}"
    )


print_range(
    "TRAIN",
    train
)

print_range(
    "VALIDATION",
    validation
)

print_range(
    "TEST",
    test
)

# ============================================
# 14. TARGET DISTRIBUTION
# ============================================

print("\n" + "=" * 60)
print("TARGET DISTRIBUTION BY SPLIT")
print("=" * 60)

for name, data in [
    ("TRAIN", train),
    ("VALIDATION", validation),
    ("TEST", test)
]:

    print(f"\n--- {name} ---")

    counts = (
        data["bottleneck_label"]
        .value_counts()
        .sort_index()
    )

    percentages = (
        data["bottleneck_label"]
        .value_counts(
            normalize=True
        )
        .sort_index()
        * 100
    )

    print("Counts:")
    print(counts)

    print("\nPercentages:")
    print(
        percentages.round(2)
    )

# ============================================
# 15. CHRONOLOGICAL CHECK
# ============================================

print("\n" + "=" * 60)
print("CHRONOLOGICAL CHECK")
print("=" * 60)

train_before_validation = (
    train["created_at"].max()
    <= validation["created_at"].min()
)

validation_before_test = (
    validation["created_at"].max()
    <= test["created_at"].min()
)

print(
    "Train before validation : "
    f"{train_before_validation}"
)

print(
    "Validation before test  : "
    f"{validation_before_test}"
)

# ============================================
# 16. REMOVE METADATA
# ============================================
#
# pr_number and created_at are NOT ML features.

model_exclude = [
    "pr_number",
    "created_at"
]

train_model = train.drop(
    columns=model_exclude
)

validation_model = validation.drop(
    columns=model_exclude
)

test_model = test.drop(
    columns=model_exclude
)

# ============================================
# 17. SAVE
# ============================================

train_model.to_csv(
    TRAIN_FILE,
    index=False
)

validation_model.to_csv(
    VAL_FILE,
    index=False
)

test_model.to_csv(
    TEST_FILE,
    index=False
)

print("\n" + "=" * 60)
print("TEMPORAL SPLIT COMPLETED")
print("=" * 60)

print("\nSaved files:")

print(TRAIN_FILE)
print(VAL_FILE)
print(TEST_FILE)

print("\nFinal model columns:")

for column in train_model.columns:
    print(f" - {column}")

print("=" * 60)