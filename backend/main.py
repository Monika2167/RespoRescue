from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.orm import Session

from scripts.predict_pr import predict_pr
from scripts.predict_health import predict_health

from backend.database import get_db
from backend.auth import create_user, verify_password
from backend.security import (
    create_access_token,
    get_current_user
)
from backend.models import User, Repository, Analysis

# Graph & Temporal API
from backend.graph_api import router as graph_routers


# =========================================================
# PYDANTIC MODELS
# =========================================================

# ============================================================
# BOTTLENECK PREDICTION MODELS
# ============================================================

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

    top_evidence: List[Evidence] = Field(
        default_factory=list
    )

    semantic_signal: Optional[str] = None
    semantic_strength: Optional[float] = None

    error: Optional[str] = None


class SignupRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    success: bool
    message: str

    user_id: Optional[int] = None
    username: Optional[str] = None
    email: Optional[str] = None

    access_token: Optional[str] = None
    token_type: Optional[str] = None


class RepositoryRequest(BaseModel):
    name: str
    github_url: str
    user_id: int


class RepositoryResponse(BaseModel):
    success: bool
    message: str

    repository_id: Optional[int] = None
    name: Optional[str] = None
    github_url: Optional[str] = None
    user_id: Optional[int] = None


class AnalysisResponse(BaseModel):
    success: bool
    message: str

    analysis_id: Optional[int] = None
    repository_id: Optional[int] = None
    pr_number: Optional[int] = None

    probability: Optional[float] = None
    prediction: Optional[str] = None
    threshold: Optional[float] = None

    semantic_signal: Optional[str] = None
    semantic_strength: Optional[float] = None

    top_evidence: List[Evidence] = Field(
        default_factory=list
    )


# =========================================================
# FASTAPI APP
# =========================================================
# ============================================================
# HEALTH FORECAST RESPONSE MODEL
# ============================================================

class HealthForecastResponse(BaseModel):
    success: bool
    date: Optional[str] = None
    forecast: Optional[float] = None
    forecast_unit: Optional[str] = None
    current_open_pr_backlog: Optional[float] = None
    current_open_issue_backlog: Optional[float] = None
    model: Optional[str] = None
    alpha: Optional[float] = None
    feature_count: Optional[int] = None
    features: List[str] = Field(default_factory=list)
    error: Optional[str] = None


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="RepoRescue API",
    description="AI-powered predictive software maintenance API",
    version="1.0.0"
)


# =========================================================
# CORS CONFIGURATION
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5174",
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# GRAPH & TEMPORAL API
# =========================================================

app.include_router(graph_routers)


# =========================================================
# ROOT
# =========================================================
# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "RepoRescue API is running",
        "status": "success"
    }


# =========================================================
# SIGNUP
# =========================================================

@app.post(
    "/auth/signup",
    response_model=AuthResponse
)
def signup(
    request: SignupRequest,
    db: Session = Depends(get_db)
):

    user, error = create_user(
        db=db,
        username=request.username,
        email=request.email,
        password=request.password
    )

    if error:
        raise HTTPException(
            status_code=400,
            detail=error
        )

    return AuthResponse(
        success=True,
        message="User registered successfully",
        user_id=user.id,
        username=user.username,
        email=user.email
    )


# =========================================================
# LOGIN
# =========================================================

@app.post(
    "/auth/login",
    response_model=AuthResponse
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):

    user = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        request.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Create JWT token
    access_token = create_access_token(
        user_id=user.id,
        email=user.email
    )

    return AuthResponse(
        success=True,
        message="Login successful",
        user_id=user.id,
        username=user.username,
        email=user.email,
        access_token=access_token,
        token_type="bearer"
    )


# =========================================================
# ADD REPOSITORY
# JWT PROTECTED
# =========================================================

@app.post(
    "/repositories",
    response_model=RepositoryResponse
)
def add_repository(
    request: RepositoryRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    # Check ownership
    if request.user_id != current_user["user_id"]:
        raise HTTPException(
            status_code=403,
            detail="You can only add repositories to your own account"
        )

    # Check user exists
    user = (
        db.query(User)
        .filter(User.id == request.user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Create repository
    repository = Repository(
        name=request.name,
        github_url=request.github_url,
        owner_id=request.user_id
    )

    db.add(repository)
    db.commit()
    db.refresh(repository)

    return RepositoryResponse(
        success=True,
        message="Repository added successfully",
        repository_id=repository.id,
        name=repository.name,
        github_url=repository.github_url,
        user_id=repository.owner_id
    )


# =========================================================
# GET USER REPOSITORIES
# JWT PROTECTED
# =========================================================

@app.get(
    "/repositories/{user_id}"
)
def get_repositories(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    # Check ownership
    if user_id != current_user["user_id"]:
        raise HTTPException(
            status_code=403,
            detail="You can only access your own repositories"
        )

    repositories = (
        db.query(Repository)
        .filter(
            Repository.owner_id == current_user["user_id"]
        )
        .all()
    )

    return {
        "success": True,
        "user_id": current_user["user_id"],
        "repositories": [
            {
                "repository_id": repo.id,
                "name": repo.name,
                "github_url": repo.github_url,
                "created_at": repo.created_at
            }
            for repo in repositories
        ]
    }


# =========================================================
# ANALYZE PR
# JWT PROTECTED
# =========================================================

@app.post(
    "/repositories/{repository_id}/analyze/{pr_number}",
    response_model=AnalysisResponse
)
def analyze_repository_pr(
    repository_id: int,
    pr_number: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    # Find repository
    repository = (
        db.query(Repository)
        .filter(
            Repository.id == repository_id
        )
        .first()
    )

    if not repository:
        raise HTTPException(
            status_code=404,
            detail="Repository not found"
        )

    # Check repository ownership
    if repository.owner_id != current_user["user_id"]:
        raise HTTPException(
            status_code=403,
            detail="You can only analyze your own repositories"
        )

    # =====================================================
    # CALL EXISTING MEMBER 1 ML PREDICTION
    # DO NOT MODIFY ML LOGIC
    # =====================================================

    result = predict_pr(pr_number)

    if not result["success"]:
        raise HTTPException(
            status_code=400,
            detail=result.get(
                "error",
                "Prediction failed"
            )
        )

    # =====================================================
    # SAVE ANALYSIS RESULT
    # =====================================================

    analysis = Analysis(
        repository_id=repository_id,
        pr_number=pr_number,
        probability=result.get("probability"),
        prediction=result.get("prediction"),
        threshold=result.get("threshold"),
        semantic_signal=result.get("semantic_signal"),
        semantic_strength=result.get("semantic_strength"),
        top_evidence=str(
            result.get("top_evidence", [])
        )
    )

    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    # =====================================================
    # RETURN RESULT
    # =====================================================

    return AnalysisResponse(
        success=True,
        message="Repository PR analyzed successfully",

        analysis_id=analysis.id,
        repository_id=repository_id,
        pr_number=pr_number,

        probability=result.get("probability"),
        prediction=result.get("prediction"),
        threshold=result.get("threshold"),

        semantic_signal=result.get(
            "semantic_signal"
        ),

        semantic_strength=result.get(
            "semantic_strength"
        ),

        top_evidence=result.get(
            "top_evidence",
            []
        )
    )


# =========================================================
# ANALYSIS HISTORY
# JWT PROTECTED
# =========================================================

@app.get(
    "/repositories/{repository_id}/analyses"
)
def get_analysis_history(
    repository_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):

    # Find repository
    repository = (
        db.query(Repository)
        .filter(
            Repository.id == repository_id
        )
        .first()
    )

    if not repository:
        raise HTTPException(
            status_code=404,
            detail="Repository not found"
        )

    # Check repository ownership
    if repository.owner_id != current_user["user_id"]:
        raise HTTPException(
            status_code=403,
            detail="You can only access your own analysis history"
        )

    # Get analyses
    analyses = (
        db.query(Analysis)
        .filter(
            Analysis.repository_id == repository_id
        )
        .order_by(
            Analysis.created_at.desc()
        )
        .all()
    )

    return {
        "success": True,
        "repository_id": repository_id,
        "repository_name": repository.name,
        "total_analyses": len(analyses),

        "analyses": [
            {
                "analysis_id": analysis.id,
                "pr_number": analysis.pr_number,
                "probability": analysis.probability,
                "prediction": analysis.prediction,
                "threshold": analysis.threshold,
                "semantic_signal": analysis.semantic_signal,
                "semantic_strength": analysis.semantic_strength,
                "top_evidence": analysis.top_evidence,
                "created_at": analysis.created_at
            }
            for analysis in analyses
        ]
    }


# =========================================================
# DIRECT ML PREDICTION
# JWT PROTECTED
# =========================================================
# ============================================================
# BOTTLENECK PREDICTION
# ============================================================

@app.get(
    "/predict/{pr_number}",
    response_model=PredictionResponse
)
def predict_pull_request(
    pr_number: int,
    current_user: dict = Depends(get_current_user)
):

    # Existing Member 1 ML logic
    result = predict_pr(pr_number)

    if not result["success"]:
        result["pr_number"] = pr_number

    return result


# ============================================================
# REPOSITORY HEALTH FORECAST
# ============================================================

@app.get(
    "/health-forecast",
    response_model=HealthForecastResponse
)
def repository_health_forecast():

    result = predict_health()

    return result
