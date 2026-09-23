from pathlib import Path

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.security import get_current_user
from backend.database import get_db
from backend.models import Repository


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/graph",
    tags=["Graph & Temporal Analysis"]
)


# ============================================================
# REPOSITORY GRAPH DATA
#
# Each selected repository must have its own graph output:
#
# data/
#   repositories/
#       <repository_id>/
#           graph/
#
# This prevents one repository's graph data from being
# accidentally served for another repository.
# ============================================================

DATA_DIR = (
    Path(__file__).resolve().parent.parent
    / "data"
)

REPOSITORY_DATA_DIR = DATA_DIR / "repositories"


# ============================================================
# GRAPH DATA FILE NAMES
# ============================================================

GRAPH_FILE_NAMES = {
    "nodes": "graph_nodes.csv",
    "edges": "graph_edges.csv",
    "impact": "impact_analysis.csv",
    "knowledge": "knowledge_concentration.csv",
    "temporal": "temporal_features.csv",
    "what_if": "what_if_results.csv",
    "developers": "developer_features.csv",
    "developer_file": "developer_file_relationships.csv",
    "file_features": "file_features.csv",
}


# ============================================================
# EXPECTED COLUMNS
# ============================================================

EXPECTED_COLUMNS = {

    "nodes": [
        "node_id",
        "node_type",
        "issue_number",
        "pr_number",
        "file_name",
        "developer",
    ],

    "edges": [
        "source",
        "target",
        "edge_type",
    ],

    "impact": [
        "source_file",
        "target_file",
        "cochange_frequency",
        "impact_weight",
    ],

    "knowledge": [
        "file_name",
        "unique_developers_per_file",
        "dominant_developer_share",
        "total_file_commits",
        "single_contributor_flag",
        "contributor_concentration",
        "dominant_developer",
    ],

    "temporal": [
        "week",
        "commits_per_week",
        "active_developers",
        "prs_per_week",
        "pr_authors",
        "files_changed_per_week",
    ],

    "what_if": [
        "scenario_type",
        "scenario_count",
        "average_affected_entities",
        "maximum_affected_entities",
        "simulated_count",
    ],

    "developers": [
        "developer",
        "files_per_developer",
        "commits_per_developer",
    ],

    "developer_file": [
        "author",
        "file_name",
    ],

    "file_features": [
        "file_name",
        "unique_developers_per_file",
        "single_contributor_flag",
    ],
}


# ============================================================
# VERIFY REPOSITORY ACCESS
# ============================================================

def verify_repository_access(
    repository_id: int,
    current_user: dict,
    db: Session
):
    repository = (
        db.query(Repository)
        .filter(
            Repository.id == repository_id,
            Repository.owner_id == current_user["user_id"]
        )
        .first()
    )

    if not repository:
        raise HTTPException(
            status_code=404,
            detail="Repository not found or access denied"
        )

    return repository


# ============================================================
# GET REPOSITORY GRAPH DIRECTORY
# ============================================================

def get_repository_graph_dir(
    repository_id: int
) -> Path:

    repository_graph_dir = (
        REPOSITORY_DATA_DIR
        / str(repository_id)
        / "graph"
    )

    return repository_graph_dir


# ============================================================
# GET REPOSITORY GRAPH FILES
# ============================================================

def get_repository_files(
    repository_id: int
):

    graph_dir = get_repository_graph_dir(
        repository_id
    )

    return {
        name: graph_dir / filename
        for name, filename in GRAPH_FILE_NAMES.items()
    }


# ============================================================
# LOAD GRAPH DATA
# ============================================================

def load_graph_data(
    name: str,
    repository_id: int
):

    files = get_repository_files(
        repository_id
    )

    if name not in files:
        raise HTTPException(
            status_code=500,
            detail=f"Unknown graph dataset: {name}"
        )

    file_path = files[name]

    # --------------------------------------------------------
    # Repository-specific output must exist.
    # --------------------------------------------------------

    if not file_path.exists():

        raise HTTPException(
            status_code=404,
            detail={
                "message": (
                    "Repository-specific graph data "
                    "is not available yet."
                ),
                "repository_id": repository_id,
                "dataset": name,
                "expected_file": str(file_path),
            }
        )

    # --------------------------------------------------------
    # Read CSV
    # --------------------------------------------------------

    try:

        df = pd.read_csv(
            file_path
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Unable to read "
                f"{file_path.name}: {str(error)}"
            )
        )

    # --------------------------------------------------------
    # Validate expected columns
    # --------------------------------------------------------

    expected = EXPECTED_COLUMNS[name]

    missing_columns = [
        column
        for column in expected
        if column not in df.columns
    ]

    if missing_columns:

        raise HTTPException(
            status_code=500,
            detail={
                "message": (
                    f"Invalid columns in "
                    f"{file_path.name}"
                ),
                "missing_columns": missing_columns,
            }
        )

    # --------------------------------------------------------
    # Keep expected columns only
    # --------------------------------------------------------

    df = df[expected]

    # --------------------------------------------------------
    # Convert NaN -> None
    # --------------------------------------------------------

    df = df.astype(object).where(
        pd.notna(df),
        None
    )

    return df


# ============================================================
# NORMAL RESPONSE
# Used for smaller datasets
# ============================================================

def dataframe_response(
    name: str,
    repository_id: int
):

    df = load_graph_data(
        name,
        repository_id
    )

    files = get_repository_files(
        repository_id
    )

    return {

        "success": True,

        "repository_id": repository_id,

        "source_file": files[name].name,

        "total_records": len(df),

        "repository_isolation": True,

        "repository_note": (
            "Data is loaded from the selected "
            "repository-specific graph dataset."
        ),

        "data": df.to_dict(
            orient="records"
        ),
    }


# ============================================================
# NODES
# graph_nodes.csv
# PAGINATION ENABLED
# ============================================================

@router.get("/nodes")
def get_graph_nodes(

    limit: int = Query(
        50,
        ge=1,
        le=500
    ),

    offset: int = Query(
        0,
        ge=0
    ),

    repository_id: int = Query(
        ...,
        ge=1
    ),

    db: Session = Depends(
        get_db
    ),

    current_user: dict = Depends(
        get_current_user
    )
):

    verify_repository_access(
        repository_id,
        current_user,
        db
    )

    df = load_graph_data(
        "nodes",
        repository_id
    )

    total_records = len(df)

    paginated_df = df.iloc[
        offset:offset + limit
    ]

    files = get_repository_files(
        repository_id
    )

    return {

        "success": True,

        "repository_id": repository_id,

        "source_file": files["nodes"].name,

        "total_records": total_records,

        "returned_records": len(
            paginated_df
        ),

        "limit": limit,

        "offset": offset,

        "repository_isolation": True,

        "repository_note": (
            "Data belongs to the authenticated "
            "user's selected repository."
        ),

        "data": paginated_df.to_dict(
            orient="records"
        ),
    }


# ============================================================
# EDGES
# graph_edges.csv
# PAGINATION ENABLED
# ============================================================

@router.get("/edges")
def get_graph_edges(

    limit: int = Query(
        50,
        ge=1,
        le=500
    ),

    offset: int = Query(
        0,
        ge=0
    ),

    repository_id: int = Query(
        ...,
        ge=1
    ),

    db: Session = Depends(
        get_db
    ),

    current_user: dict = Depends(
        get_current_user
    )
):

    verify_repository_access(
        repository_id,
        current_user,
        db
    )

    df = load_graph_data(
        "edges",
        repository_id
    )

    total_records = len(df)

    paginated_df = df.iloc[
        offset:offset + limit
    ]

    files = get_repository_files(
        repository_id
    )

    return {

        "success": True,

        "repository_id": repository_id,

        "source_file": files["edges"].name,

        "total_records": total_records,

        "returned_records": len(
            paginated_df
        ),

        "limit": limit,

        "offset": offset,

        "repository_isolation": True,

        "repository_note": (
            "Data belongs to the authenticated "
            "user's selected repository."
        ),

        "data": paginated_df.to_dict(
            orient="records"
        ),
    }


# ============================================================
# IMPACT ANALYSIS
# impact_analysis.csv
# PAGINATION ENABLED
# ============================================================

@router.get("/impact")
def get_graph_impact(

    limit: int = Query(
        50,
        ge=1,
        le=500
    ),

    offset: int = Query(
        0,
        ge=0
    ),

    repository_id: int = Query(
        ...,
        ge=1
    ),

    db: Session = Depends(
        get_db
    ),

    current_user: dict = Depends(
        get_current_user
    )
):

    verify_repository_access(
        repository_id,
        current_user,
        db
    )

    df = load_graph_data(
        "impact",
        repository_id
    )

    total_records = len(df)

    paginated_df = df.iloc[
        offset:offset + limit
    ]

    files = get_repository_files(
        repository_id
    )

    return {

        "success": True,

        "repository_id": repository_id,

        "source_file": files["impact"].name,

        "total_records": total_records,

        "returned_records": len(
            paginated_df
        ),

        "limit": limit,

        "offset": offset,

        "repository_isolation": True,

        "repository_note": (
            "Impact data belongs to the "
            "authenticated user's selected repository."
        ),

        "data": paginated_df.to_dict(
            orient="records"
        ),
    }


# ============================================================
# KNOWLEDGE CONCENTRATION
# knowledge_concentration.csv
# PAGINATION ENABLED
# ============================================================

@router.get("/knowledge-concentration")
def get_knowledge_concentration(

    limit: int = Query(
        50,
        ge=1,
        le=500
    ),

    offset: int = Query(
        0,
        ge=0
    ),

    repository_id: int = Query(
        ...,
        ge=1
    ),

    db: Session = Depends(
        get_db
    ),

    current_user: dict = Depends(
        get_current_user
    )
):

    verify_repository_access(
        repository_id,
        current_user,
        db
    )

    df = load_graph_data(
        "knowledge",
        repository_id
    )

    total_records = len(df)

    paginated_df = df.iloc[
        offset:offset + limit
    ]

    files = get_repository_files(
        repository_id
    )

    return {

        "success": True,

        "repository_id": repository_id,

        "source_file": files["knowledge"].name,

        "total_records": total_records,

        "returned_records": len(
            paginated_df
        ),

        "limit": limit,

        "offset": offset,

        "repository_isolation": True,

        "repository_note": (
            "Knowledge concentration data belongs "
            "to the authenticated user's selected repository."
        ),

        "data": paginated_df.to_dict(
            orient="records"
        ),
    }


# ============================================================
# TEMPORAL FEATURES
# temporal_features.csv
# ============================================================

@router.get("/temporal")
def get_temporal_features(

    repository_id: int = Query(
        ...,
        ge=1
    ),

    db: Session = Depends(
        get_db
    ),

    current_user: dict = Depends(
        get_current_user
    )
):

    verify_repository_access(
        repository_id,
        current_user,
        db
    )

    return dataframe_response(
        "temporal",
        repository_id
    )


# ============================================================
# WHAT-IF ANALYSIS
# what_if_results.csv
# ============================================================

@router.get("/what-if")
def get_what_if_results(

    repository_id: int = Query(
        ...,
        ge=1
    ),

    db: Session = Depends(
        get_db
    ),

    current_user: dict = Depends(
        get_current_user
    )
):

    verify_repository_access(
        repository_id,
        current_user,
        db
    )

    return dataframe_response(
        "what_if",
        repository_id
    )


# ============================================================
# DEVELOPER FEATURES
# developer_features.csv
# ============================================================

@router.get("/developers")
def get_developer_features(

    repository_id: int = Query(
        ...,
        ge=1
    ),

    db: Session = Depends(
        get_db
    ),

    current_user: dict = Depends(
        get_current_user
    )
):

    verify_repository_access(
        repository_id,
        current_user,
        db
    )

    return dataframe_response(
        "developers",
        repository_id
    )


# ============================================================
# DEVELOPER-FILE RELATIONSHIPS
# developer_file_relationships.csv
# PAGINATION ENABLED
# ============================================================

@router.get("/developer-file")
def get_developer_file_relationships(

    limit: int = Query(
        50,
        ge=1,
        le=500
    ),

    offset: int = Query(
        0,
        ge=0
    ),

    repository_id: int = Query(
        ...,
        ge=1
    ),

    db: Session = Depends(
        get_db
    ),

    current_user: dict = Depends(
        get_current_user
    )
):

    verify_repository_access(
        repository_id,
        current_user,
        db
    )

    df = load_graph_data(
        "developer_file",
        repository_id
    )

    total_records = len(df)

    paginated_df = df.iloc[
        offset:offset + limit
    ]

    files = get_repository_files(
        repository_id
    )

    return {

        "success": True,

        "repository_id": repository_id,

        "source_file": (
            files["developer_file"].name
        ),

        "total_records": total_records,

        "returned_records": len(
            paginated_df
        ),

        "limit": limit,

        "offset": offset,

        "repository_isolation": True,

        "repository_note": (
            "Developer-file data belongs to "
            "the authenticated user's selected repository."
        ),

        "data": paginated_df.to_dict(
            orient="records"
        ),
    }


# ============================================================
# FILE FEATURES
# file_features.csv
# ============================================================

@router.get("/file-features")
def get_file_features(

    repository_id: int = Query(
        ...,
        ge=1
    ),

    db: Session = Depends(
        get_db
    ),

    current_user: dict = Depends(
        get_current_user
    )
):

    verify_repository_access(
        repository_id,
        current_user,
        db
    )

    return dataframe_response(
        "file_features",
        repository_id
    )