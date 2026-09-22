import os
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import User, GitHubConnection, Repository
from backend.security import (
    SECRET_KEY,
    ALGORITHM,
    get_current_user,
)


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

# github_oauth.py is inside backend/
# .env is inside scripts/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, "scripts", ".env")

load_dotenv(ENV_PATH)


GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

GITHUB_AUTHORIZE_URL = (
    "https://github.com/login/oauth/authorize"
)

GITHUB_TOKEN_URL = (
    "https://github.com/login/oauth/access_token"
)

GITHUB_API_URL = "https://api.github.com"

GITHUB_REDIRECT_URI = (
    "http://127.0.0.1:8001/auth/github/callback"
)


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/auth/github",
    tags=["GitHub OAuth"]
)


# =========================================================
# HELPER - GITHUB HEADERS
# =========================================================

def github_headers(access_token: str) -> dict:
    return {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "RepoRescue",
    }


# =========================================================
# HELPER - CHECK CONFIGURATION
# =========================================================

def ensure_github_oauth_configured():
    if not GITHUB_CLIENT_ID:
        raise HTTPException(
            status_code=500,
            detail="GitHub Client ID is not configured"
        )

    if not GITHUB_CLIENT_SECRET:
        raise HTTPException(
            status_code=500,
            detail="GitHub Client Secret is not configured"
        )


# =========================================================
# GITHUB LOGIN
# =========================================================

@router.get("/login")
def github_login(token: str):

    ensure_github_oauth_configured()

    # -----------------------------------------------------
    # Decode RepoRescue JWT
    # -----------------------------------------------------

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token"
            )

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )

    # -----------------------------------------------------
    # Create OAuth State
    # -----------------------------------------------------

    state_payload = {
        "user_id": user_id,
        "purpose": "github_oauth",
        "exp": (
            datetime.now(timezone.utc)
            + timedelta(minutes=10)
        )
    }

    state = jwt.encode(
        state_payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    # -----------------------------------------------------
    # GitHub Authorization URL
    # -----------------------------------------------------

    params = {
        "client_id": GITHUB_CLIENT_ID,
        "redirect_uri": GITHUB_REDIRECT_URI,
        "scope": "repo",
        "state": state
    }

    github_url = (
        f"{GITHUB_AUTHORIZE_URL}?"
        f"{urlencode(params)}"
    )

    return RedirectResponse(
        url=github_url
    )


# =========================================================
# GITHUB CALLBACK
# =========================================================

@router.get("/callback")
async def github_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db)
):

    ensure_github_oauth_configured()

    # -----------------------------------------------------
    # Validate OAuth State
    # -----------------------------------------------------

    try:

        payload = jwt.decode(
            state,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        if payload.get("purpose") != "github_oauth":
            raise HTTPException(
                status_code=400,
                detail="Invalid OAuth state"
            )

        user_id = payload.get("user_id")

        if not user_id:
            raise HTTPException(
                status_code=400,
                detail="Invalid OAuth state user"
            )

    except JWTError:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired OAuth state"
        )

    # -----------------------------------------------------
    # Find RepoRescue User
    # -----------------------------------------------------

    user = (
        db.query(User)
        .filter(
            User.id == int(user_id)
        )
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="RepoRescue user not found"
        )

    # -----------------------------------------------------
    # Exchange Authorization Code
    # -----------------------------------------------------

    token_data = {
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": code,
        "redirect_uri": GITHUB_REDIRECT_URI
    }

    try:

        async with httpx.AsyncClient(
            timeout=20.0
        ) as client:

            token_response = await client.post(
                GITHUB_TOKEN_URL,
                data=token_data,
                headers={
                    "Accept": "application/json"
                }
            )

    except httpx.RequestError as exc:

        raise HTTPException(
            status_code=502,
            detail=f"GitHub token request failed: {str(exc)}"
        )

    if token_response.status_code != 200:

        raise HTTPException(
            status_code=400,
            detail=(
                "Failed to exchange GitHub authorization code. "
                f"GitHub status: {token_response.status_code}"
            )
        )

    token_json = token_response.json()

    # GitHub may return an error object even with HTTP 200
    if token_json.get("error"):
        raise HTTPException(
            status_code=400,
            detail=(
                "GitHub OAuth error: "
                f"{token_json.get('error_description', token_json.get('error'))}"
            )
        )

    access_token = token_json.get(
        "access_token"
    )

    if not access_token:

        raise HTTPException(
            status_code=400,
            detail="GitHub access token was not received"
        )

    # -----------------------------------------------------
    # Get GitHub User Information
    # -----------------------------------------------------

    headers = github_headers(access_token)

    try:

        async with httpx.AsyncClient(
            timeout=20.0
        ) as client:

            github_user_response = await client.get(
                f"{GITHUB_API_URL}/user",
                headers=headers
            )

    except httpx.RequestError as exc:

        raise HTTPException(
            status_code=502,
            detail=f"Failed to contact GitHub: {str(exc)}"
        )

    if github_user_response.status_code != 200:

        try:
            github_error = github_user_response.json()
        except Exception:
            github_error = {}

        raise HTTPException(
            status_code=400,
            detail=(
                "Failed to retrieve GitHub user. "
                f"GitHub status: {github_user_response.status_code}. "
                f"{github_error.get('message', '')}"
            ).strip()
        )

    github_user = github_user_response.json()

    github_user_id = str(
        github_user.get("id")
    )

    github_username = github_user.get(
        "login"
    )

    if (
        not github_user_id
        or not github_username
    ):

        raise HTTPException(
            status_code=400,
            detail="Invalid GitHub user information"
        )

    # -----------------------------------------------------
    # Save / Update GitHub Connection
    # -----------------------------------------------------

    connection = (
        db.query(GitHubConnection)
        .filter(
            GitHubConnection.user_id == user.id
        )
        .first()
    )

    if connection:

        connection.github_user_id = (
            github_user_id
        )

        connection.github_username = (
            github_username
        )

        connection.access_token = (
            access_token
        )

        connection.updated_at = (
            datetime.now(timezone.utc)
        )

    else:

        connection = GitHubConnection(
            user_id=user.id,
            github_user_id=github_user_id,
            github_username=github_username,
            access_token=access_token
        )

        db.add(connection)

    db.commit()

    # -----------------------------------------------------
    # Redirect back to Frontend
    # -----------------------------------------------------

    frontend_url = (
        "http://localhost:5174"
        "?github=connected"
    )

    return RedirectResponse(
        url=frontend_url
    )


# =========================================================
# GET AUTHORIZED GITHUB REPOSITORIES
# =========================================================

@router.get("/repositories")
async def get_github_repositories(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # -----------------------------------------------------
    # Current RepoRescue User
    # -----------------------------------------------------

    user_id = current_user["user_id"]

    # -----------------------------------------------------
    # Get ONLY this user's GitHub connection
    # -----------------------------------------------------

    connection = (
        db.query(GitHubConnection)
        .filter(
            GitHubConnection.user_id == user_id
        )
        .first()
    )

    if not connection:

        raise HTTPException(
            status_code=404,
            detail="GitHub account is not connected"
        )

    access_token = connection.access_token

    if not access_token:

        raise HTTPException(
            status_code=401,
            detail="GitHub access token is missing"
        )

    headers = github_headers(
        access_token
    )

    # -----------------------------------------------------
    # Get Authorized Repositories
    # -----------------------------------------------------

    repositories = []

    page = 1

    try:

        async with httpx.AsyncClient(
            timeout=30.0
        ) as client:

            while True:

                response = await client.get(
                    f"{GITHUB_API_URL}/user/repos",
                    headers=headers,
                    params={
                        "visibility": "all",
                        "affiliation": (
                            "owner,collaborator,"
                            "organization_member"
                        ),
                        "sort": "updated",
                        "direction": "desc",
                        "per_page": 100,
                        "page": page
                    }
                )

                # -------------------------------------------------
                # Invalid / expired GitHub token
                # -------------------------------------------------

                if response.status_code == 401:

                    raise HTTPException(
                        status_code=401,
                        detail=(
                            "GitHub authorization has expired "
                            "or the access token is invalid. "
                            "Please reconnect your GitHub account."
                        )
                    )

                # -------------------------------------------------
                # Forbidden / permission problem
                # -------------------------------------------------

                if response.status_code == 403:

                    try:
                        github_error = response.json()
                    except Exception:
                        github_error = {}

                    raise HTTPException(
                        status_code=403,
                        detail=(
                            "GitHub denied repository access. "
                            f"{github_error.get('message', 'Permission denied')}"
                        )
                    )

                # -------------------------------------------------
                # Other GitHub API errors
                # -------------------------------------------------

                if response.status_code != 200:

                    try:
                        github_error = response.json()
                    except Exception:
                        github_error = {}

                    raise HTTPException(
                        status_code=502,
                        detail=(
                            "GitHub repository request failed. "
                            f"GitHub status: {response.status_code}. "
                            f"{github_error.get('message', 'Unknown GitHub error')}"
                        )
                    )

                page_repositories = response.json()

                if not isinstance(
                    page_repositories,
                    list
                ):
                    raise HTTPException(
                        status_code=502,
                        detail=(
                            "GitHub returned an unexpected "
                            "repository response"
                        )
                    )

                repositories.extend(
                    page_repositories
                )

                # GitHub returned fewer than 100,
                # therefore this is the final page.
                if len(page_repositories) < 100:
                    break

                page += 1

                # Safety limit
                if page > 20:
                    break

    except HTTPException:
        raise

    except httpx.RequestError as exc:

        raise HTTPException(
            status_code=502,
            detail=(
                "Unable to connect to GitHub: "
                f"{str(exc)}"
            )
        )

    # -----------------------------------------------------
    # Safe Repository Response
    # -----------------------------------------------------

    repo_list = []

    for repo in repositories:

        repo_list.append(
            {
                "id": repo.get("id"),

                "name": repo.get(
                    "name"
                ),

                "full_name": repo.get(
                    "full_name"
                ),

                "private": repo.get(
                    "private"
                ),

                "html_url": repo.get(
                    "html_url"
                ),

                "owner": (
                    repo.get(
                        "owner",
                        {}
                    ).get(
                        "login"
                    )
                )
            }
        )

    return {
        "github_connected": True,
        "total_repositories": len(repo_list),
        "repositories": repo_list
    }


# =========================================================
# SELECT GITHUB REPOSITORY
# =========================================================

@router.post("/select-repository")
async def select_repository(
    github_repo_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # -----------------------------------------------------
    # Current RepoRescue User
    # -----------------------------------------------------

    user_id = current_user["user_id"]

    # -----------------------------------------------------
    # Get ONLY current user's GitHub connection
    # -----------------------------------------------------

    connection = (
        db.query(GitHubConnection)
        .filter(
            GitHubConnection.user_id == user_id
        )
        .first()
    )

    if not connection:

        raise HTTPException(
            status_code=404,
            detail="GitHub account is not connected"
        )

    access_token = connection.access_token

    if not access_token:

        raise HTTPException(
            status_code=401,
            detail="GitHub access token is missing"
        )

    headers = github_headers(
        access_token
    )

    # -----------------------------------------------------
    # Verify Repository Access
    # -----------------------------------------------------

    try:

        async with httpx.AsyncClient(
            timeout=20.0
        ) as client:

            repo_response = await client.get(
                f"{GITHUB_API_URL}/repositories/{github_repo_id}",
                headers=headers
            )

    except httpx.RequestError as exc:

        raise HTTPException(
            status_code=502,
            detail=(
                "Unable to connect to GitHub: "
                f"{str(exc)}"
            )
        )

    if repo_response.status_code == 401:

        raise HTTPException(
            status_code=401,
            detail=(
                "GitHub authorization has expired "
                "or the access token is invalid"
            )
        )

    if repo_response.status_code != 200:

        try:
            github_error = repo_response.json()
        except Exception:
            github_error = {}

        raise HTTPException(
            status_code=403,
            detail=(
                "Repository is not accessible by the "
                "connected GitHub account. "
                f"{github_error.get('message', '')}"
            ).strip()
        )

    repo = repo_response.json()

    # -----------------------------------------------------
    # Repository Information
    # -----------------------------------------------------

    repo_name = repo.get(
        "name"
    )

    repo_url = repo.get(
        "html_url"
    )

    repo_owner = (
        repo.get(
            "owner",
            {}
        ).get(
            "login"
        )
    )

    repo_full_name = repo.get(
        "full_name"
    )

    if (
        not repo_name
        or not repo_url
        or not repo_owner
        or not repo_full_name
    ):

        raise HTTPException(
            status_code=400,
            detail="Invalid repository information"
        )

    # -----------------------------------------------------
    # Save Repository
    # -----------------------------------------------------

    existing_repository = (
        db.query(Repository)
        .filter(
            Repository.owner_id == user_id,
            Repository.github_url == repo_url
        )
        .first()
    )

    if existing_repository:

        repository = existing_repository

    else:

        repository = Repository(
            name=repo_name,
            github_url=repo_url,
            owner_id=user_id
        )

        db.add(repository)

        db.commit()

        db.refresh(repository)

    # -----------------------------------------------------
    # Return Workspace Information
    # -----------------------------------------------------

    return {
        "success": True,

        "message": (
            "Repository selected successfully"
        ),

        "repository": {
            "id": repository.id,

            "name": repository.name,

            "github_url": repository.github_url,

            "github_owner": repo_owner,

            "github_full_name": repo_full_name,

            "owner_id": repository.owner_id
        },

        "workspace": {
            "repository_id": repository.id,

            "repository_name": repository.name,

            "github_full_name": repo_full_name
        }
    }