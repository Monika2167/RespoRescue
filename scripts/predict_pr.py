from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Optional

import joblib
import numpy as np
import pandas as pd
import requests
from sentence_transformers import SentenceTransformer


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    BASE_DIR
    / "data"
    / "ml"
    / "model_artifacts"
    / "combined_logistic_regression.joblib"
)

SCALER_PATH = (
    BASE_DIR
    / "data"
    / "ml"
    / "model_artifacts"
    / "structured_scaler.joblib"
)

FEATURES_PATH = (
    BASE_DIR
    / "data"
    / "ml"
    / "model_artifacts"
    / "model_features.joblib"
)

CONFIG_PATH = (
    BASE_DIR
    / "data"
    / "ml"
    / "model_artifacts"
    / "model_config.joblib"
)


# ============================================================
# GITHUB API
# ============================================================

GITHUB_API_URL = "https://api.github.com"

GITHUB_HEADERS_BASE = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


# ============================================================
# LOAD MODEL ARTIFACTS
# ============================================================

model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
structured_features = joblib.load(FEATURES_PATH)
config = joblib.load(CONFIG_PATH)

threshold = float(config["threshold"])


# ============================================================
# LOAD EMBEDDING MODEL
# ============================================================

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# ============================================================
# EXPECTED FEATURES
# ============================================================

EXPECTED_FEATURES = [
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
    "has_file_activity_24h",
]


# ============================================================
# GITHUB HELPERS
# ============================================================

def github_headers(access_token: str):
    return {
        **GITHUB_HEADERS_BASE,
        "Authorization": f"Bearer {access_token}",
    }


def github_get(
    url: str,
    access_token: str,
    params: Optional[dict] = None,
):
    response = requests.get(
        url,
        headers=github_headers(access_token),
        params=params,
        timeout=30,
    )

    if response.status_code >= 400:
        try:
            detail = response.json().get(
                "message",
                response.text,
            )
        except Exception:
            detail = response.text

        raise RuntimeError(
            f"GitHub API error {response.status_code}: {detail}"
        )

    return response.json()


# ============================================================
# PARSE REPOSITORY
# ============================================================

def normalize_repo_name(repo_full_name: str) -> str:

    if not repo_full_name:
        raise ValueError(
            "GitHub repository name is required."
        )

    repo_full_name = repo_full_name.strip()

    if repo_full_name.startswith(
        "https://github.com/"
    ):
        repo_full_name = repo_full_name[
            len("https://github.com/"):
        ]

    elif repo_full_name.startswith(
        "http://github.com/"
    ):
        repo_full_name = repo_full_name[
            len("http://github.com/"):
        ]

    repo_full_name = repo_full_name.rstrip("/")

    if repo_full_name.endswith(".git"):
        repo_full_name = repo_full_name[:-4]

    parts = repo_full_name.split("/")

    if len(parts) != 2:
        raise ValueError(
            "Invalid GitHub repository. "
            "Expected owner/repository."
        )

    owner, repo = parts

    if not owner or not repo:
        raise ValueError(
            "Invalid GitHub repository."
        )

    return f"{owner}/{repo}"


# ============================================================
# FETCH PR + FIRST 24-HOUR ACTIVITY
# ============================================================

def fetch_pr_data(
    repo_full_name: str,
    pr_number: int,
    access_token: str,
):

    repo_full_name = normalize_repo_name(
        repo_full_name
    )

    pr_number = int(pr_number)

    if pr_number <= 0:
        raise ValueError(
            "PR number must be greater than zero."
        )

    # --------------------------------------------------------
    # PR
    # --------------------------------------------------------

    pr_url = (
        f"{GITHUB_API_URL}/repos/"
        f"{repo_full_name}/pulls/{pr_number}"
    )

    pr = github_get(
        pr_url,
        access_token,
    )

    created_at_text = pr.get("created_at")

    if not created_at_text:
        raise RuntimeError(
            "GitHub PR does not contain created_at."
        )

    created_at = datetime.fromisoformat(
        created_at_text.replace(
            "Z",
            "+00:00",
        )
    )

    cutoff = created_at + timedelta(
        hours=24
    )

    title = pr.get("title") or ""
    body = pr.get("body") or ""

    # --------------------------------------------------------
    # COMMITS
    # --------------------------------------------------------

    commit_rows = []

    page = 1

    while True:

        commits_url = (
            f"{GITHUB_API_URL}/repos/"
            f"{repo_full_name}/pulls/"
            f"{pr_number}/commits"
        )

        page_data = github_get(
            commits_url,
            access_token,
            params={
                "per_page": 100,
                "page": page,
            },
        )

        if not page_data:
            break

        for commit in page_data:

            commit_sha = commit.get("sha")

            commit_info = commit.get(
                "commit",
                {},
            )

            commit_author = commit_info.get(
                "author"
            ) or {}

            commit_date_text = (
                commit_author.get("date")
            )

            if not commit_date_text:
                continue

            commit_date = datetime.fromisoformat(
                commit_date_text.replace(
                    "Z",
                    "+00:00",
                )
            )

            if commit_date <= cutoff:

                commit_rows.append(
                    {
                        "sha": commit_sha,
                        "author": (
                            commit.get("author", {})
                            or {}
                        ).get(
                            "login"
                        )
                        or commit_author.get(
                            "name"
                        )
                        or "unknown",
                        "date": commit_date,
                    }
                )

        if len(page_data) < 100:
            break

        page += 1

        # Safety limit
        if page > 20:
            break

    # --------------------------------------------------------
    # UNIQUE COMMITS
    # --------------------------------------------------------

    unique_commits = {}

    for row in commit_rows:

        sha = row["sha"]

        if sha:
            unique_commits[sha] = row

    commit_rows = list(
        unique_commits.values()
    )

    # --------------------------------------------------------
    # COMMIT DETAILS
    # --------------------------------------------------------

    additions = 0
    deletions = 0

    changed_files = set()

    commit_authors = set()

    for row in commit_rows:

        sha = row["sha"]

        if not sha:
            continue

        detail_url = (
            f"{GITHUB_API_URL}/repos/"
            f"{repo_full_name}/commits/{sha}"
        )

        detail = github_get(
            detail_url,
            access_token,
        )

        stats = detail.get(
            "stats",
            {},
        )

        additions += int(
            stats.get(
                "additions",
                0,
            )
            or 0
        )

        deletions += int(
            stats.get(
                "deletions",
                0,
            )
            or 0
        )

        for file_info in (
            detail.get(
                "files",
                []
            )
            or []
        ):

            filename = file_info.get(
                "filename"
            )

            if filename:
                changed_files.add(
                    filename
                )

        author = row.get(
            "author"
        )

        if author:
            commit_authors.add(
                author
            )

    # ========================================================
    # STRUCTURED FEATURES
    # ========================================================

    title_words = (
        title.split()
        if title.strip()
        else []
    )

    body_words = (
        body.split()
        if body.strip()
        else []
    )

    commits_24h = len(
        commit_rows
    )

    commit_authors_24h = len(
        commit_authors
    )

    files_changed_24h = len(
        changed_files
    )

    total_changes_24h = (
        additions
        + deletions
    )

    changes_per_commit_24h = (
        total_changes_24h / commits_24h
        if commits_24h > 0
        else 0.0
    )

    files_per_commit_24h = (
        files_changed_24h / commits_24h
        if commits_24h > 0
        else 0.0
    )

    deletion_ratio_24h = (
        deletions / total_changes_24h
        if total_changes_24h > 0
        else 0.0
    )

    features = {
        "title_length": len(title),
        "body_length": len(body),
        "title_word_count": len(title_words),
        "body_word_count": len(body_words),
        "is_draft": int(
            bool(
                pr.get(
                    "draft",
                    False
                )
            )
        ),
        "commits_24h": commits_24h,
        "commit_authors_24h": commit_authors_24h,
        "files_changed_24h": files_changed_24h,
        "additions_24h": additions,
        "deletions_24h": deletions,
        "total_changes_24h": total_changes_24h,
        "changes_per_commit_24h":
            changes_per_commit_24h,
        "files_per_commit_24h":
            files_per_commit_24h,
        "deletion_ratio_24h":
            deletion_ratio_24h,
        "has_commit_activity_24h": int(
            commits_24h > 0
        ),
        "has_file_activity_24h": int(
            files_changed_24h > 0
        ),
    }

    return {
        "pr": pr,
        "title": title,
        "body": body,
        "created_at": created_at,
        "features": features,
    }


# ============================================================
# BUILD EMBEDDING
# ============================================================

def build_text_embedding(
    title: str,
    body: str,
):

    text = (
        f"{title}\n{body}"
    ).strip()

    embedding = embedding_model.encode(
        [text],
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    return np.asarray(
        embedding[0],
        dtype=float,
    )


# ============================================================
# PREDICT
# ============================================================

def predict_pr(
    pr_number: int,
    repo_full_name: Optional[str] = None,
    access_token: Optional[str] = None,
):

    try:

        if not repo_full_name:
            return {
                "success": False,
                "pr_number": int(
                    pr_number
                ),
                "error": (
                    "GitHub repository is required "
                    "for live PR prediction."
                ),
            }

        if not access_token:
            return {
                "success": False,
                "pr_number": int(
                    pr_number
                ),
                "error": (
                    "GitHub access token is required "
                    "for live PR prediction."
                ),
            }

        # ----------------------------------------------------
        # FETCH LIVE DATA
        # ----------------------------------------------------

        live_data = fetch_pr_data(
            repo_full_name=repo_full_name,
            pr_number=pr_number,
            access_token=access_token,
        )

        features = live_data[
            "features"
        ]

        # ----------------------------------------------------
        # FEATURE ORDER CHECK
        # ----------------------------------------------------

        missing = [
            feature
            for feature in structured_features
            if feature not in features
        ]

        if missing:

            raise RuntimeError(
                "Missing required model features: "
                + ", ".join(missing)
            )

        # ----------------------------------------------------
        # STRUCTURED VECTOR
        # ----------------------------------------------------

        structured_vector = np.array(
            [
                features[feature]
                for feature in structured_features
            ],
            dtype=float,
        ).reshape(
            1,
            -1,
        )

        structured_scaled = scaler.transform(
            structured_vector
        )

        # ----------------------------------------------------
        # SEMANTIC EMBEDDING
        # ----------------------------------------------------

        embedding = build_text_embedding(
            live_data["title"],
            live_data["body"],
        )

        embedding_vector = embedding.reshape(
            1,
            -1,
        )

        # ----------------------------------------------------
        # FINAL MODEL INPUT
        # ----------------------------------------------------

        X = np.concatenate(
            [
                structured_scaled,
                embedding_vector,
            ],
            axis=1,
        )

        # ----------------------------------------------------
        # PREDICTION
        # ----------------------------------------------------

        probability = float(
            model.predict_proba(
                X
            )[0, 1]
        )

        prediction = (
            "Potential Bottleneck"
            if probability >= threshold
            else "Low Bottleneck Risk"
        )

        # ----------------------------------------------------
        # STRUCTURED EXPLAINABILITY
        # ----------------------------------------------------

        coefficients = np.asarray(
            model.coef_[0]
        )

        scaled_values = (
            structured_scaled[0]
        )

        structured_contributions = []

        for index, feature in enumerate(
            structured_features
        ):

            contribution = float(
                scaled_values[index]
                * coefficients[index]
            )

            structured_contributions.append(
                {
                    "feature": feature,
                    "contribution": contribution,
                    "direction": (
                        "increases bottleneck risk"
                        if contribution > 0
                        else "reduces bottleneck risk"
                    ),
                }
            )

        structured_contributions.sort(
            key=lambda item: abs(
                item["contribution"]
            ),
            reverse=True,
        )

        top_evidence = (
            structured_contributions[:6]
        )

        # ----------------------------------------------------
        # SEMANTIC CONTRIBUTION
        # ----------------------------------------------------

        embedding_coefficients = (
            coefficients[
                len(structured_features):
            ]
        )

        semantic_strength = float(
            np.dot(
                embedding,
                embedding_coefficients,
            )
        )

        if semantic_strength > 0:
            semantic_signal = "Positive"
        elif semantic_strength < 0:
            semantic_signal = "Negative"
        else:
            semantic_signal = "Neutral"

        # ----------------------------------------------------
        # RESULT
        # ----------------------------------------------------

        return {
            "success": True,

            "repo_full_name": normalize_repo_name(
                repo_full_name
            ),

            "pr_number": int(
                pr_number
            ),

            "title": live_data[
                "title"
            ],

            "author": (
                live_data["pr"]
                .get("user", {})
                or {}
            ).get(
                "login"
            ),

            "created_at": (
                live_data["created_at"]
                .isoformat()
            ),

            "probability": probability,

            "probability_percent": (
                probability * 100
            ),

            "prediction": prediction,

            "threshold": threshold,

            "top_evidence": top_evidence,

            "semantic_signal": semantic_signal,

            "semantic_strength": semantic_strength,

            "features": features,
        }

    except Exception as exc:

        return {
            "success": False,
            "pr_number": int(
                pr_number
            ),
            "error": str(exc),
        }