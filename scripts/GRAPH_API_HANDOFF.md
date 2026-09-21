# RepoRescue - Graph & Temporal Analysis Handoff

## Member 2 Responsibilities

Member 2 handles:

- Repository relationship graph
- Developer-file relationship analysis
- Knowledge concentration
- Maintainer bottleneck analysis
- Impact propagation
- Temporal repository analysis
- What-if simulation
- Root-cause candidate evidence
- Early-warning signals
- Feature audit and validation

---

# 1. Repository Graph

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

### Validation

- Duplicate node IDs: 0
- Duplicate edges: 0
- Self-loops: 0
- Invalid source references: 0
- Invalid target references: 0

---

# 2. Developer-File Relationship Analysis

### Script

`scripts/developer_file_relationships.py`

### Output

`data/graph/developer_file_relationships.csv`

### Current Output

- Relationships: 169,834
- Developers: 485
- Files: 11,200

### Main Features

- author
- file_name
- commit_count
- additions
- deletions
- total_changes
- pr_count
- first_activity
- last_activity
- activity_duration_days
- activity_frequency
- relationship_strength

These features represent observed developer-file contribution relationships.

---

# 3. Knowledge Concentration

### Script

`scripts/knowledge_concentration.py`

### Output

`data/graph/knowledge_concentration.csv`

### Current Output

- Files: 11,200
- HIGH risk signals: 130
- MEDIUM risk signals: 594
- LOW risk signals: 10,476
- Single-contributor files: 3,518

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

These are analytical concentration signals and are not proof of failure or future developer unavailability.

---

# 4. Maintainer Bottleneck Analysis

### Script

`scripts/maintainer_bottlenecks.py`

### Output

`data/graph/maintainer_bottlenecks.csv`

### Current Output

- Developers: 485

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

The bottleneck score combines observed file, commit and change contribution shares.

This is supporting analytical evidence and should not be interpreted as confirmed ownership or a prediction of developer availability.

---

# 5. Impact Propagation

### Script

`scripts/impact_propagation.py`

### Outputs

- `data/graph/impact_analysis.csv`
- `data/graph/impact_propagation.csv`

### Impact Types

- DIRECT
- RELATIONSHIP_BASED
- HISTORICAL

### Current Historical Impact Analysis

- Relationships: 558,908

### Supported Evidence Paths

- PR -> Commit
- Commit -> File
- Commit -> Developer
- PR -> File
- PR -> Developer
- PR -> Issue
- File -> File through historical co-change

Historical File -> File relationships represent observed historical co-change and do not prove source-code dependency or causality.

### Impact Query

`scripts/impact_query.py`

The query module can start from a repository entity such as a PR and traverse connected graph relationships to identify potentially affected entities.

Impact results represent graph evidence and potential propagation, not confirmed causal impact.

---

# 6. Temporal Repository Analysis

### Script

`scripts/temporal_analysis.py`

### Output

`data/graph/temporal_features.csv`

### Current Output

- Weeks: 43
- Period: available historical repository data
- Missing values: 0
- Duplicate rows: 0

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
- issues_created_per_week
- issues_updated_per_week
- issues_closed_per_week
- unresolved_issues
- additions_per_week
- deletions_per_week
- change_volume_per_week
- active_developer_file_relationships
- active_developers_in_files
- new_developer_file_relationships
- repository_activity_volume
- four_week_activity_average
- activity_change_pct
- activity_pattern_signal

The rolling activity comparison uses current and previous historical periods and avoids using future observations as input.

---

# 7. What-If Simulation

### Script

`scripts/what_if_simulation.py`

### Output

`data/graph/what_if_simulation.csv`

### Current Output

- Total simulation rows: 186,034
- DEVELOPER_UNAVAILABLE: 169,834
- FILE_CHANGE: 11,200
- PR_DELAY: 5,000

### Scenario Types

#### DEVELOPER_UNAVAILABLE

Simulates removal of a developer's observed contribution from developer-file relationships and recalculates contribution concentration.

#### FILE_CHANGE

Identifies observed developers, relationships and affected repository areas associated with a selected file.

The scenario does not fabricate a new code change magnitude.

#### PR_DELAY

Identifies observed files, developers and issues associated with a delayed pull request.

### Important Limitation

What-if scenarios are simulations based on observed repository relationships.

They are not predictions of actual developer behavior, future code changes, or exact failure probabilities.

Projected or estimated outcomes must be clearly labelled as simulation results.

---

# 8. Root-Cause Candidate Evidence

### Script

`scripts/root_cause_candidates.py`

### Output

`data/graph/root_cause_candidates.csv`

### Current Output

- Candidate evidence rows: 441,950

### Main Evidence

- commit_sha
- commit_author
- commit_date
- pr_number
- title
- file_name
- changes
- additions
- deletions
- file_commit_count
- file_pr_count
- recency_score
- change_score
- frequency_score
- candidate_score

The candidate score combines observed recency, change magnitude and repeated file activity.

### Important Limitation

These are **root-cause candidates**, not confirmed root causes.

The system does not claim that a particular commit, PR, file or developer definitely caused an issue.

---

# 9. Early-Warning System

### Script

`scripts/early_warning_system.py`

### Output

`data/graph/early_warning_signals.csv`

### Current Output

- Warning signals: 9,263
- HIGH: 141
- MEDIUM: 9,105
- LOW: 17

### Signal Sources

#### Temporal Signals

- Unusual repository activity
- Activity spikes
- Growing unresolved issue backlog
- Large numbers of new developer-file relationships

#### Knowledge Concentration

- HIGH concentration
- MEDIUM concentration
- Dominant developer share

#### Developer-File Relationships

- Strong developer-file relationships
- High dependency concentration

These signals are heuristic supporting evidence for an early-warning system.

They are not final ML predictions.

---

# 10. Feature Audit

### Script

`scripts/feature_audit.py`

### Output

`data/graph/feature_audit.csv`

### Current Audit

- Total audit rows: 29
- Used feature records: 25
- Intentionally excluded records: 4

The feature audit documents:

- Source dataset
- Source columns
- Derived feature
- Usage status
- Reason for inclusion/exclusion

Fields related primarily to NLP/text modelling are intentionally excluded from Member 2 analysis and remain available for Member 1's ML/NLP work.

---

# 11. Final Validation

### Script

`scripts/validate_member2_outputs.py`

### Validation Results

All 11 Member 2 output files were successfully validated.

| Output | Status |
|---|---|
| graph_nodes.csv | PASS |
| graph_edges.csv | PASS |
| developer_file_relationships.csv | PASS |
| knowledge_concentration.csv | PASS |
| maintainer_bottlenecks.csv | PASS |
| impact_analysis.csv | PASS |
| temporal_features.csv | PASS |
| what_if_simulation.csv | PASS |
| root_cause_candidates.csv | PASS |
| early_warning_signals.csv | PASS |
| feature_audit.csv | PASS |

### Validation Summary

- Files checked: 11
- Files passed: 11
- Files failed: 0
- Duplicate output rows: 0 across validated outputs

Some output tables naturally contain missing values because certain fields do not apply to every entity or scenario. These are not treated as validation failures.

---

# 12. Member 1 Compatibility

Member 2 outputs provide graph and temporal evidence that can be consumed by the project backend, dashboard and ML pipeline.

Member 2 does not modify:

- ML model
- ML feature engineering
- Prediction threshold
- Prediction logic
- ML artifacts

Member 1 remains responsible for the final prediction system.

Member 2 outputs should be treated as supporting graph and temporal evidence.

---

# 13. Dashboard Usage

Member 3 can use the CSV outputs for:

- Repository graph visualization
- Developer contribution view
- Knowledge concentration view
- Maintainer bottleneck view
- Impact propagation view
- Weekly activity trends
- What-if analysis
- Root-cause candidate view
- Early-warning signal view

The CSV outputs provide the current integration interface for Member 2.

---

# 14. Integration Interface

Member 2 outputs are CSV-based and can be loaded using pandas, PostgreSQL import tools or backend data-processing functions.

Example:

```python
import pandas as pd

temporal = pd.read_csv("data/graph/temporal_features.csv")
knowledge = pd.read_csv("data/graph/knowledge_concentration.csv")
developer_file = pd.read_csv(
    "data/graph/developer_file_relationships.csv"
)