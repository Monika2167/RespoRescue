from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

from scripts.predict_pr import predict_pr


class Evidence(BaseModel):
    feature: str
    description: str
    contribution: float
    direction: str
    explanation: str


class PredictionResponse(BaseModel):
    success: bool
    pr_number: int
    probability: Optional[float] = None
    probability_percent: Optional[float] = None
    prediction: Optional[str] = None
    threshold: Optional[float] = None
    top_evidence: List[Evidence] = Field(default_factory=list)
    semantic_signal: Optional[str] = None
    semantic_strength: Optional[float] = None
    error: Optional[str] = None


app = FastAPI(
    title="RepoRescue API",
    description="AI-powered predictive software maintenance API",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "RepoRescue API is running",
        "status": "success"
    }


@app.get(
    "/predict/{pr_number}",
    response_model=PredictionResponse
)
def predict_pull_request(pr_number: int):

    result = predict_pr(pr_number)

    # Handle PRs for which prediction data is unavailable
    if not result["success"]:
        result["pr_number"] = pr_number

    return result