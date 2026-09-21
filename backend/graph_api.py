from pathlib import Path

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query

from backend.security import get_current_user


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/graph",
    tags=["Graph & Temporal Analysis"]
)


# ============================================================
# GRAPH DATA DIRECTORY
# ============================================================

GRAPH_DIR = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "graph"
)


# ============================================================
# GRAPH DATA FILES
# ============================================================

FILES = {
    "nodes": GRAPH_DIR / "graph_nodes.csv",
    "edges": GRAPH_DIR / "graph_edges.csv",
    "impact": GRAPH_DIR / "impact_analysis.csv",
    "knowledge": GRAPH_DIR / "knowledge_concentration.csv",
    "temporal": GRAPH_DIR / "temporal_features.csv",
    "what_if": GRAPH_DIR / "what_if_results.csv",
    "developers": GRAPH_DIR / "developer_features.csv",
    "developer_file": GRAPH_DIR / "developer_file_relationships.csv",
    "file_features": GRAPH_DIR / "file_features.csv",
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
        "commit_sha",
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
        "file_name",
        "dominant_developer",
        "dominant_developer_share",
        "total_commits",
        "unique_developers",
        "files_losing_dominant_contributor",
        "files_with_no_remaining_contributor",
        "remaining_contributor_share",
        "high_concentration_flag",
    ],

    "developers": [
        "developer",
        "files_per_developer",
        "commits_per_developer",
    ],

    "developer_file": [
        "commit_sha",
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
# LOAD GRAPH DATA
# ============================================================

def load_graph_data(name: str):

    file_path = FILES[name]

    # Check whether file exists
    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=(
                f"Graph output file not found: "
                f"{file_path.name}"
            )
        )

    # Read CSV
    try:
        df = pd.read_csv(file_path)

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Unable to read "
                f"{file_path.name}: {str(error)}"
            )
        )

    # Check expected columns
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

    # Keep only expected columns
    df = df[expected]

    # Convert NaN -> None
    df = df.astype(object).where(
        pd.notna(df),
        None
    )

    return df


# ============================================================
# NORMAL RESPONSE
# Used for smaller datasets
# ============================================================

def dataframe_response(name: str):

    df = load_graph_data(name)

    return {
        "success": True,

        "source_file": FILES[name].name,

        "total_records": len(df),

        "repository_isolation": False,

        "repository_note": (
            "This graph output does not contain "
            "a repository identifier. "
            "The current dataset is therefore "
            "not independently filterable "
            "by repository."
        ),

        "data": df.to_dict(
            orient="records"
        ),
    }


# ============================================================
# NODES
# graph_nodes.csv
# Around 37,682 records
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

    current_user: dict = Depends(
        get_current_user
    )
):

    df = load_graph_data("nodes")

    total_records = len(df)

    paginated_df = df.iloc[
        offset:offset + limit
    ]

    return {

        "success": True,

        "source_file": FILES["nodes"].name,

        "total_records": total_records,

        "returned_records": len(
            paginated_df
        ),

        "limit": limit,

        "offset": offset,

        "repository_isolation": False,

        "repository_note": (
            "This graph output does not contain "
            "a repository identifier. "
            "The current dataset is therefore "
            "not independently filterable "
            "by repository."
        ),

        "data": paginated_df.to_dict(
            orient="records"
        ),
    }


# ============================================================
# EDGES
# graph_edges.csv
# Around 478,773 records
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

    current_user: dict = Depends(
        get_current_user
    )
):

    df = load_graph_data("edges")

    total_records = len(df)

    paginated_df = df.iloc[
        offset:offset + limit
    ]

    return {

        "success": True,

        "source_file": FILES["edges"].name,

        "total_records": total_records,

        "returned_records": len(
            paginated_df
        ),

        "limit": limit,

        "offset": offset,

        "repository_isolation": False,

        "repository_note": (
            "This graph output does not contain "
            "a repository identifier. "
            "The current dataset is therefore "
            "not independently filterable "
            "by repository."
        ),

        "data": paginated_df.to_dict(
            orient="records"
        ),
    }


# ============================================================
# IMPACT ANALYSIS
# impact_analysis.csv
# Around 558,908 records
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

    current_user: dict = Depends(
        get_current_user
    )
):

    df = load_graph_data("impact")

    total_records = len(df)

    paginated_df = df.iloc[
        offset:offset + limit
    ]

    return {

        "success": True,

        "source_file": FILES["impact"].name,

        "total_records": total_records,

        "returned_records": len(
            paginated_df
        ),

        "limit": limit,

        "offset": offset,

        "repository_isolation": False,

        "repository_note": (
            "This graph output does not contain "
            "a repository identifier. "
            "The current dataset is therefore "
            "not independently filterable "
            "by repository."
        ),

        "data": paginated_df.to_dict(
            orient="records"
        ),
    }


# ============================================================
# KNOWLEDGE CONCENTRATION
# knowledge_concentration.csv
# Around 11,200 records
# ============================================================
@router.get("/knowledge-concentration")
def get_knowledge_concentration(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    df = load_graph_data("knowledge")

    total_records = len(df)
    paginated_df = df.iloc[offset:offset + limit]

    return {
        "success": True,
        "source_file": FILES["knowledge"].name,
        "total_records": total_records,
        "returned_records": len(paginated_df),
        "limit": limit,
        "offset": offset,
        "repository_isolation": False,
        "repository_note": (
            "This graph output does not contain a repository identifier. "
            "The current dataset is therefore not independently filterable "
            "by repository."
        ),
        "data": paginated_df.to_dict(orient="records"),
    }


# ============================================================
# TEMPORAL FEATURES
# temporal_features.csv
# Around 36 records
# ============================================================

@router.get("/temporal")
def get_temporal_features(

    current_user: dict = Depends(
        get_current_user
    )
):

    return dataframe_response(
        "temporal"
    )


# ============================================================
# WHAT-IF ANALYSIS
# what_if_results.csv
# Around 11,200 records
# ============================================================

@router.get("/what-if")
def get_what_if_results(

    current_user: dict = Depends(
        get_current_user
    )
):

    return dataframe_response(
        "what_if"
    )


# ============================================================
# DEVELOPER FEATURES
# developer_features.csv
# Around 485 records
# ============================================================

@router.get("/developers")
def get_developer_features(

    current_user: dict = Depends(
        get_current_user
    )
):

    return dataframe_response(
        "developers"
    )


# ============================================================
# DEVELOPER-FILE RELATIONSHIPS
# developer_file_relationships.csv
# Around 169,834 records
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

    current_user: dict = Depends(
        get_current_user
    )
):

    df = load_graph_data(
        "developer_file"
    )

    total_records = len(df)

    paginated_df = df.iloc[
        offset:offset + limit
    ]

    return {

        "success": True,

        "source_file": (
            FILES["developer_file"].name
        ),

        "total_records": total_records,

        "returned_records": len(
            paginated_df
        ),

        "limit": limit,

        "offset": offset,

        "repository_isolation": False,

        "repository_note": (
            "This graph output does not contain "
            "a repository identifier. "
            "The current dataset is therefore "
            "not independently filterable "
            "by repository."
        ),

        "data": paginated_df.to_dict(
            orient="records"
        ),
    }


# ============================================================
# FILE FEATURES
# file_features.csv
# Around 11,200 records
# ============================================================

@router.get("/file-features")
def get_file_features(

    current_user: dict = Depends(
        get_current_user
    )
):

    return dataframe_response(
        "file_features"
    )