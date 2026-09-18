import pandas as pd
import networkx as nx
from pathlib import Path

# ============================================================
# Paths
# ============================================================
BASE_DIR = Path(__file__).resolve().parents[1]

NODES_FILE = BASE_DIR / "data" / "graph" / "graph_nodes.csv"
EDGES_FILE = BASE_DIR / "data" / "graph" / "graph_edges.csv"


# ============================================================
# Load graph outputs
# ============================================================
nodes = pd.read_csv(NODES_FILE)
edges = pd.read_csv(EDGES_FILE)

print("Graph files loaded successfully.")

print("\nNode rows:", len(nodes))
print("Edge rows:", len(edges))


# ============================================================
# Basic column validation
# ============================================================
required_node_columns = [
    "node_id",
    "node_type"
]

required_edge_columns = [
    "source",
    "target",
    "edge_type"
]

print("\n--- Column Validation ---")

print(
    "Node columns present:",
    all(column in nodes.columns for column in required_node_columns)
)

print(
    "Edge columns present:",
    all(column in edges.columns for column in required_edge_columns)
)


# ============================================================
# Missing value validation
# ============================================================
print("\n--- Missing Values ---")

print(
    "Node missing values:",
    int(nodes[required_node_columns].isna().sum().sum())
)

print(
    "Edge missing values:",
    int(edges[required_edge_columns].isna().sum().sum())
)


# ============================================================
# Duplicate validation
# ============================================================
print("\n--- Duplicate Validation ---")

duplicate_nodes = nodes.duplicated(
    subset=["node_id"]
).sum()

duplicate_edges = edges.duplicated(
    subset=["source", "target", "edge_type"]
).sum()

print(
    "Duplicate node IDs:",
    int(duplicate_nodes)
)

print(
    "Duplicate edges:",
    int(duplicate_edges)
)


# ============================================================
# Self-loop validation
# ============================================================
print("\n--- Self-loop Validation ---")

self_loops = (
    edges["source"]
    == edges["target"]
).sum()

print(
    "Self-loops:",
    int(self_loops)
)


# ============================================================
# Node reference validation
# ============================================================
print("\n--- Node Reference Validation ---")

node_ids = set(
    nodes["node_id"]
    .astype(str)
)

source_ids = set(
    edges["source"]
    .astype(str)
)

target_ids = set(
    edges["target"]
    .astype(str)
)

invalid_sources = source_ids - node_ids
invalid_targets = target_ids - node_ids

print(
    "Invalid source references:",
    len(invalid_sources)
)

print(
    "Invalid target references:",
    len(invalid_targets)
)


# ============================================================
# Node type validation
# ============================================================
print("\n--- Nodes By Type ---")

print(
    nodes["node_type"]
    .value_counts()
)


# ============================================================
# Edge type validation
# ============================================================
print("\n--- Edges By Type ---")

print(
    edges["edge_type"]
    .value_counts()
)


# ============================================================
# Build NetworkX graph
# ============================================================
graph = nx.DiGraph()

for _, row in nodes.iterrows():

    graph.add_node(
        str(row["node_id"]),
        node_type=row["node_type"]
    )


for _, row in edges.iterrows():

    graph.add_edge(
        str(row["source"]),
        str(row["target"]),
        edge_type=row["edge_type"]
    )


# ============================================================
# Connected components
# ============================================================
print("\n--- Connectivity ---")

undirected_graph = graph.to_undirected()

components = list(
    nx.connected_components(
        undirected_graph
    )
)

print(
    "Connected components:",
    len(components)
)

largest_component = max(
    [len(component) for component in components],
    default=0
)

print(
    "Largest component nodes:",
    largest_component
)


# ============================================================
# Relationship validation
# ============================================================
print("\n--- Relationship Validation ---")

expected_relationships = [
    "ISSUE_HAS_PR",
    "PR_HAS_COMMIT",
    "COMMIT_MODIFIES_FILE",
    "DEVELOPER_AUTHORED_COMMIT",
    "DEVELOPER_AUTHORED_PR"
]

actual_relationships = set(
    edges["edge_type"].astype(str)
)

for relationship in expected_relationships:

    count = (
        edges["edge_type"]
        == relationship
    ).sum()

    print(
        relationship + ":",
        int(count)
    )


# ============================================================
# Final validation summary
# ============================================================
print("\n================================================")
print("GRAPH VALIDATION COMPLETED")
print("================================================")

print(
    "Nodes:",
    len(nodes)
)

print(
    "Edges:",
    len(edges)
)

print(
    "Duplicate nodes:",
    int(duplicate_nodes)
)

print(
    "Duplicate edges:",
    int(duplicate_edges)
)

print(
    "Self-loops:",
    int(self_loops)
)

print(
    "Invalid source references:",
    len(invalid_sources)
)

print(
    "Invalid target references:",
    len(invalid_targets)
)

print(
    "Connected components:",
    len(components)
)

print(
    "Largest component:",
    largest_component
)

print("\nValidation finished successfully.")
print("\n--- Connectivity ---")

graph = nx.DiGraph()

for _, row in nodes.iterrows():
    graph.add_node(
        str(row["node_id"]),
        node_type=row["node_type"]
    )

for _, row in edges.iterrows():
    graph.add_edge(
        str(row["source"]),
        str(row["target"]),
        edge_type=row["edge_type"]
    )

undirected_graph = graph.to_undirected()

components = list(nx.connected_components(undirected_graph))

print("Connected components:", len(components))

largest_component = max(
    [len(component) for component in components],
    default=0
)

print("Largest component nodes:", largest_component)


print("\n--- Relationship Validation ---")

expected_relationships = [
    "ISSUE_HAS_PR",
    "PR_HAS_COMMIT",
    "COMMIT_MODIFIES_FILE",
    "DEVELOPER_AUTHORED_COMMIT",
    "DEVELOPER_AUTHORED_PR"
]

for relationship in expected_relationships:
    count = (edges["edge_type"] == relationship).sum()
    print(relationship + ":", int(count))


print("\n================================================")
print("GRAPH VALIDATION COMPLETED")
print("================================================")

print("Nodes:", len(nodes))
print("Edges:", len(edges))
print("Duplicate nodes:", int(duplicate_nodes))
print("Duplicate edges:", int(duplicate_edges))
print("Self-loops:", int(self_loops))
print("Invalid source references:", len(invalid_sources))
print("Invalid target references:", len(invalid_targets))
print("Connected components:", len(components))
print("Largest component:", largest_component)

print("\nValidation finished successfully.")