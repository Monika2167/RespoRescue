# RepoRescue - Graph & Temporal Analysis Handoff

## Member 2 Responsibilities

Member 2 handles:
- Repository relationship graph
- Developer-file analysis
- Knowledge concentration
- Maintainer bottleneck detection
- Impact propagation
- Temporal analysis
- What-if simulation

---

## 1. Repository Graph

### Script
`scripts/graph_builder.py`

### Outputs
- `data/graph/graph_nodes.csv`
- `data/graph/graph_edges.csv`

### Node Types
- Issue
- PR
- Commit
- File
- Developer

### Relationship Types
- ISSUE_HAS_PR
- PR_HAS_COMMIT
- COMMIT_MODIFIES_FILE
- DEVELOPER_AUTHORED_COMMIT
- DEVELOPER_AUTHORED_PR

### Current Graph
- Nodes: 37,682
- Edges: 478,773

The graph uses relationships available in the real dataset. Missing relationships are not invented.

---

## 2. Developer-File Analysis

### Script
`scripts/developer_file_graph.py`

### Outputs
- `data/graph/developer_features.csv`
- `data/graph/developer_file_relationships.csv`
- `data/graph/file_features.csv`

### Main Features
- files_per_developer
- commits_per_developer
- unique_developers_per_file
- single_contributor_flag

These features describe actual developer-file contribution relationships.

---

## 3. Knowledge Concentration

### Script
`scripts/knowledge_concentration.py`

### Output
`data/graph/knowledge_concentration.csv`

### Main Columns
- file_name
- unique_developers_per_file
- dominant_developer_share
- dominant_developer_commit_count
- total_file_commits
- single_contributor_flag
- contributor_concentration
- dominant_developer
- concentration_risk_signal

### Risk Signal
- HIGH: dominant share >= 0.75 and at least 5 commits
- MEDIUM: dominant share >= 0.50 and at least 3 commits
- LOW: otherwise

This is a measurable concentration signal, not proof that a failure will occur.

---

## 4. Maintainer Bottleneck Detection

### Script
`scripts/maintainer_bottlenecks.py`

### Output
`data/graph/maintainer_bottlenecks.csv`

### Main Columns
- developer
- files_touched
- commits
- changes
- file_share
- commit_share
- change_share
- developer_concentration
- bottleneck_score
- risk_level
- evidence

The bottleneck score combines file, commit and change contribution shares.

This represents contribution concentration and should not be interpreted as confirmed ownership or future developer unavailability.

---

## 5. Impact Propagation

### Script
`scripts/impact_propagation.py`

### Outputs
- `data/graph/impact_analysis.csv`
- `data/graph/impact_propagation.csv`

### Impact Types
- DIRECT
- RELATIONSHIP_BASED
- HISTORICAL

### Examples
- PR -> Commit
- Commit -> File
- Commit -> Developer
- PR -> File
- PR -> Developer
- PR -> Issue
- File -> File through historical co-change

Historical File -> File relationships represent historical co-change, not confirmed code dependency.

---

## 6. Temporal Analysis

### Script
`scripts/temporal_analysis.py`

### Output
`data/graph/temporal_features.csv`

### Main Features
- week
- commits_per_week
- active_developers
- prs_per_week
- pr_authors
- files_changed_per_week
- pr_created_per_week
- pr_updated_per_week
- pr_closed_per_week
- pr_merged_per_week
- unresolved_prs
- additions_per_week
- deletions_per_week
- change_volume_per_week

Current analysis covers 43 weeks of available data.

---

## 7. What-If Simulation

### Script
`scripts/what_if_simulation.py`

### Outputs
- `data/graph/what_if_results.csv`
- `data/graph/what_if_scenarios.csv`

### Scenario Types
- DEVELOPER_UNAVAILABLE
- FILE_CHANGE

The developer scenario measures how contribution concentration changes when a developer's contribution is removed from the calculation.

The simulation is hypothetical and does not claim that a developer will actually leave or become unavailable.

---

## 8. Graph Validation

### Script
`scripts/validate_graph_outputs.py`

### Validation Results
- Nodes: 37,682
- Edges: 478,773
- Missing values: 0
- Duplicate node IDs: 0
- Duplicate edges: 0
- Self-loops: 0
- Invalid source references: 0
- Invalid target references: 0

The graph passed the available integrity checks.

---

## 9. Member 1 Compatibility

Member 2 outputs provide graph and temporal signals that can be consumed by the project dashboard or backend.

Member 2 does not modify:
- ML model
- ML features
- prediction threshold
- prediction logic
- ML artifacts

Member 1 prediction endpoint remains:

`GET /predict/{pr_number}`

Graph and temporal outputs can be used as supporting repository-level analysis.

---

## 10. Dashboard Usage

Member 3 can use the CSV outputs for dashboard components such as:

- Repository graph visualization
- Developer contribution view
- Knowledge concentration view
- Maintainer bottleneck view
- Impact propagation view
- Weekly activity trends
- What-if analysis

The CSV files are the current handoff interface for Member 2 analysis.

---

## 11. Limitations

- Analysis is based only on relationships available in the collected dataset.
- Missing Issue -> PR relationships are not artificially created.
- Historical co-change does not prove source-code dependency.
- Concentration and bottleneck scores are analytical signals.
- What-if scenarios are simulations, not predictions of actual developer behavior.
- Temporal results depend on the available timestamps and repository history.