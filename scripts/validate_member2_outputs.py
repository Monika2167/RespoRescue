import os
import pandas as pd

GRAPH_DIR = os.path.join("data", "graph")

files = {
    "Graph Nodes": "graph_nodes.csv",
    "Graph Edges": "graph_edges.csv",
    "Developer-File": "developer_file_relationships.csv",
    "Knowledge Concentration": "knowledge_concentration.csv",
    "Maintainer Bottlenecks": "maintainer_bottlenecks.csv",
    "Impact Analysis": "impact_analysis.csv",
    "Temporal Features": "temporal_features.csv",
    "What-If Simulation": "what_if_simulation.csv",
    "Root Cause Candidates": "root_cause_candidates.csv",
    "Early Warning Signals": "early_warning_signals.csv",
    "Feature Audit": "feature_audit.csv",
}

print("=" * 65)
print("REPORESCUE - MEMBER 2 FINAL VALIDATION")
print("=" * 65)

passed = 0
failed = 0

for name, filename in files.items():
    path = os.path.join(GRAPH_DIR, filename)

    if not os.path.exists(path):
        print(f"[FAIL] {name}: {filename} not found")
        failed += 1
        continue

    try:
        df = pd.read_csv(path)

        rows = len(df)
        cols = len(df.columns)
        duplicates = df.duplicated().sum()
        missing = df.isna().sum().sum()

        if rows == 0:
            print(f"[FAIL] {name}: empty file")
            failed += 1
            continue

        if duplicates > 0:
            print(f"[WARN] {name}: {duplicates} duplicate rows")

        print(
            f"[PASS] {name}: "
            f"{rows:,} rows | {cols} columns | "
            f"missing={missing:,} | duplicates={duplicates:,}"
        )

        passed += 1

    except Exception as e:
        print(f"[FAIL] {name}: {e}")
        failed += 1

print("\n" + "=" * 65)
print(f"FILES PASSED : {passed}")
print(f"FILES FAILED : {failed}")
print("=" * 65)

if failed == 0:
    print("FINAL VALIDATION: PASSED")
else:
    print("FINAL VALIDATION: CHECK FAILED FILES")
