import pandas as pd
import networkx as nx
from pathlib import Path


# -----------------------------
# Paths
# -----------------------------
DATA_DIR = Path("data/cleaned")
OUTPUT_DIR = Path("data/graph")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# -----------------------------
# Load cleaned datasets
# -----------------------------
issues = pd.read_csv(DATA_DIR / "issues_clean.csv", dtype=str)
pull_requests = pd.read_csv(DATA_DIR / "pull_requests_clean.csv", dtype=str)
commits = pd.read_csv(DATA_DIR / "commits_clean.csv", dtype=str)
files = pd.read_csv(DATA_DIR / "files_clean.csv", dtype=str)

print("Datasets loaded successfully.")
print(f"Issues: {len(issues)}")
print(f"Pull Requests: {len(pull_requests)}")
print(f"Commits: {len(commits)}")
print(f"File changes: {len(files)}")


# -----------------------------
# Create directed graph
# -----------------------------
G = nx.DiGraph()


# -----------------------------
# Add Issue nodes
# -----------------------------
for issue_number in issues["issue_number"].dropna().unique():
    G.add_node(
        f"ISSUE_{issue_number}",
        node_type="Issue",
        issue_number=issue_number
    )


# -----------------------------
# Add PR nodes
# -----------------------------
for pr_number in pull_requests["pr_number"].dropna().unique():
    G.add_node(
        f"PR_{pr_number}",
        node_type="PR",
        pr_number=pr_number
    )


# -----------------------------
# Add Commit nodes
# -----------------------------
for sha in commits["commit_sha"].dropna().unique():
    G.add_node(
        f"COMMIT_{sha}",
        node_type="Commit",
        commit_sha=sha
    )


# -----------------------------
# Add File nodes
# -----------------------------
for file_name in files["file_name"].dropna().unique():
    G.add_node(
        f"FILE_{file_name}",
        node_type="File",
        file_name=file_name
    )


# -----------------------------
# Add Developer nodes
# -----------------------------
developers = set()

developers.update(
    pull_requests["author"].dropna().unique()
)

developers.update(
    commits["author"].dropna().unique()
)

for developer in developers:
    G.add_node(
        f"DEV_{developer}",
        node_type="Developer",
        developer=developer
    )


# -----------------------------
# Issue -> PR relationships
# -----------------------------
issue_pr = pd.read_csv(
    "data/issue_pr_relationships.csv",
    dtype=str
)

for _, row in issue_pr.iterrows():

    issue = row["issue_number"]
    pr = row["pr_number"]

    issue_node = f"ISSUE_{issue}"
    pr_node = f"PR_{pr}"

    if issue_node in G and pr_node in G:
        G.add_edge(
            issue_node,
            pr_node,
            edge_type="ISSUE_HAS_PR"
        )


# -----------------------------
# PR -> Commit relationships
# -----------------------------
for _, row in commits.iterrows():

    pr = row["pr_number"]
    sha = row["commit_sha"]

    if pd.notna(pr) and pd.notna(sha):

        pr_node = f"PR_{pr}"
        commit_node = f"COMMIT_{sha}"

        if pr_node in G and commit_node in G:
            G.add_edge(
                pr_node,
                commit_node,
                edge_type="PR_HAS_COMMIT"
            )


# -----------------------------
# Commit -> File relationships
# -----------------------------
for _, row in files.iterrows():

    sha = row["commit_sha"]
    file_name = row["file_name"]

    if pd.notna(sha) and pd.notna(file_name):

        commit_node = f"COMMIT_{sha}"
        file_node = f"FILE_{file_name}"

        if commit_node in G and file_node in G:
            G.add_edge(
                commit_node,
                file_node,
                edge_type="COMMIT_MODIFIES_FILE"
            )


# -----------------------------
# Developer -> PR relationships
# -----------------------------
for _, row in pull_requests.iterrows():

    developer = row["author"]
    pr = row["pr_number"]

    if pd.notna(developer) and pd.notna(pr):

        dev_node = f"DEV_{developer}"
        pr_node = f"PR_{pr}"

        if dev_node in G and pr_node in G:
            G.add_edge(
                dev_node,
                pr_node,
                edge_type="DEVELOPER_AUTHORED_PR"
            )


# -----------------------------
# Developer -> Commit relationships
# -----------------------------
for _, row in commits.iterrows():

    developer = row["author"]
    sha = row["commit_sha"]

    if pd.notna(developer) and pd.notna(sha):

        dev_node = f"DEV_{developer}"
        commit_node = f"COMMIT_{sha}"

        if dev_node in G and commit_node in G:
            G.add_edge(
                dev_node,
                commit_node,
                edge_type="DEVELOPER_AUTHORED_COMMIT"
            )


# -----------------------------
# Save graph nodes
# -----------------------------
node_rows = []

for node_id, attributes in G.nodes(data=True):

    row = {
        "node_id": node_id,
        "node_type": attributes.get("node_type")
    }

    row.update(
        {
            key: value
            for key, value in attributes.items()
            if key != "node_type"
        }
    )

    node_rows.append(row)


nodes_df = pd.DataFrame(node_rows)
nodes_df.to_csv(
    OUTPUT_DIR / "graph_nodes.csv",
    index=False
)


# -----------------------------
# Save graph edges
# -----------------------------
edge_rows = []

for source, target, attributes in G.edges(data=True):

    edge_rows.append(
        {
            "source": source,
            "target": target,
            "edge_type": attributes.get("edge_type")
        }
    )


edges_df = pd.DataFrame(edge_rows)

edges_df.to_csv(
    OUTPUT_DIR / "graph_edges.csv",
    index=False
)


# -----------------------------
# Summary
# -----------------------------
print("\nGraph built successfully!")
print(f"Nodes: {G.number_of_nodes()}")
print(f"Edges: {G.number_of_edges()}")

print("\nNodes by type:")
print(
    nodes_df["node_type"]
    .value_counts()
)

print("\nEdges by type:")
print(
    edges_df["edge_type"]
    .value_counts()
)

print("\nOutput files:")
print(OUTPUT_DIR / "graph_nodes.csv")
print(OUTPUT_DIR / "graph_edges.csv")