C:\Users\kanim\OneDrive\Desktop\RespoRescue# RepoRescue ML API — Member 3 Handoff

## Purpose

RepoRescue ML predicts whether a Pull Request (PR) is likely to remain unresolved beyond 7 days.

## FastAPI Endpoint

GET /predict/{pr_number}

Example:

GET /predict/333333

Local API:

http://127.0.0.1:8000

Swagger:

http://127.0.0.1:8000/docs

## ML Model

Final model:

Scaled Combined Logistic Regression

Input:

- 16 structured features
- 384 semantic embedding features
- 400 total features

Decision threshold:

0.57

## API Response

The API returns:

- success
- pr_number
- probability
- probability_percent
- prediction
- threshold
- top_evidence
- semantic_signal
- semantic_strength

## Example

PR #333333:

Probability: 86.86%

Prediction:

Potential Bottleneck

PR #333999:

Probability: 14.44%

Prediction:

Lower Bottleneck Risk

## Model Artifacts

Location:

data/ml/model_artifacts/

Files:

- combined_logistic_regression.joblib
- structured_scaler.joblib
- model_features.joblib
- model_config.joblib

Prediction module:

scripts/predict_pr.py

## How FastAPI Uses the ML Model

FastAPI imports:

from scripts.predict_pr import predict_pr

Then:

result = predict_pr(pr_number)

The backend does not retrain the model for every request.

## Start API

From the RepoRescue project root:

python -m uvicorn backend.main:app --reload

## Frontend Integration

The frontend can call:

GET /predict/{pr_number}

Example:

http://127.0.0.1:8000/predict/333333

The returned JSON can be used to display:

- PR number
- bottleneck probability
- prediction
- evidence
- semantic analysis

## Important

Do not modify the following without coordinating with Member 1:

- model threshold
- feature order
- scaler
- embedding model
- model artifacts
- prediction feature definitions

## Current Status

ML Model: READY

Prediction Module: READY

Explainability: READY

Model Artifacts: READY

FastAPI Endpoint: READY

Pydantic Response: READY

Swagger Testing: READY

Member 3 Integration: READY TO START

## Architecture

GitHub
↓
Repository Data
↓
ML Prediction Module
↓
FastAPI
↓
JSON Response
↓
React Dashboard

## Member 3 Checklist

- FastAPI can import predict_pr
- Model artifacts are available
- /predict/{pr_number} works
- Swagger works
- Frontend can consume the JSON
- Private repository access is protected
- Repository ownership is verified
- ML threshold remains 0.57


RepoRescue ML is ready for backend and frontend integration.
