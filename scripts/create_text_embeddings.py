import os
import pandas as pd
import numpy as np

from sentence_transformers import SentenceTransformer


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FEATURE_PATH = os.path.join(
    BASE_DIR,
    "data",
    "features",
    "pr_24h_prediction_features.csv"
)

PR_PATH = os.path.join(
    BASE_DIR,
    "data",
    "preprocessed",
    "pull_requests_preprocessed.csv"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "data",
    "nlp",
    "embeddings"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 60)
print("REPORESCUE - SEMANTIC TEXT EMBEDDINGS")
print("=" * 60)

features = pd.read_csv(FEATURE_PATH)
prs = pd.read_csv(PR_PATH)

print(f"Prediction feature rows : {len(features)}")
print(f"PR rows                 : {len(prs)}")


# ============================================================
# PREPARE TEXT
# ============================================================

prs["title"] = prs["title"].fillna("").astype(str)
prs["body"] = prs["body"].fillna("").astype(str)

# Give title slightly more importance by placing it first.
prs["text"] = (
    prs["title"].str.strip()
    + " "
    + prs["body"].str.strip()
)

# Only use PRs present in our prediction dataset.
text_data = features[["pr_number"]].merge(
    prs[["pr_number", "text"]],
    on="pr_number",
    how="left"
)

text_data["text"] = text_data["text"].fillna("")

print(f"Text records prepared : {len(text_data)}")


# ============================================================
# LOAD SEMANTIC MODEL
# ============================================================

print("\nLoading embedding model...")

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

print("Embedding model loaded.")


# ============================================================
# GENERATE EMBEDDINGS
# ============================================================

print("\nGenerating embeddings...")
print("This may take some time on CPU.")

embeddings = model.encode(
    text_data["text"].tolist(),
    batch_size=32,
    show_progress_bar=True,
    convert_to_numpy=True,
    normalize_embeddings=True
)


# ============================================================
# VALIDATION
# ============================================================

print("\n" + "=" * 60)
print("EMBEDDING INFORMATION")
print("=" * 60)

print(f"Number of PRs       : {embeddings.shape[0]}")
print(f"Embedding dimension : {embeddings.shape[1]}")
print(f"Data type           : {embeddings.dtype}")

print(
    f"NaN values          : "
    f"{np.isnan(embeddings).sum()}"
)

print(
    f"Infinite values     : "
    f"{np.isinf(embeddings).sum()}"
)

print(
    f"Minimum value       : "
    f"{embeddings.min():.6f}"
)

print(
    f"Maximum value       : "
    f"{embeddings.max():.6f}"
)


# ============================================================
# SAVE EMBEDDINGS
# ============================================================

embedding_path = os.path.join(
    OUTPUT_DIR,
    "pr_text_embeddings.npy"
)

np.save(
    embedding_path,
    embeddings
)


# ============================================================
# SAVE PR MAPPING
# ============================================================

mapping = text_data[["pr_number"]].copy()

mapping_path = os.path.join(
    OUTPUT_DIR,
    "embedding_pr_numbers.csv"
)

mapping.to_csv(
    mapping_path,
    index=False
)


# ============================================================
# SAVE MODEL INFORMATION
# ============================================================

model_info = pd.DataFrame(
    {
        "model": ["all-MiniLM-L6-v2"],
        "embedding_dimension": [embeddings.shape[1]],
        "normalization": ["L2 normalized"],
        "records": [embeddings.shape[0]]
    }
)

model_info.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "embedding_model_info.csv"
    ),
    index=False
)


# ============================================================
# COMPLETION
# ============================================================

print("\nSaved:")
print(embedding_path)
print(mapping_path)

print("\n" + "=" * 60)
print("SEMANTIC EMBEDDING STEP COMPLETED")
print("=" * 60)