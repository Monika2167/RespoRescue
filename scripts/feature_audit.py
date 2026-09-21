import os
import pandas as pd

GRAPH_DIR = os.path.join("data", "graph")
os.makedirs(GRAPH_DIR, exist_ok=True)

rows = [
    # Impact Graph
    ["Impact Graph", "commits_clean.csv", "commit_sha,pr_number,author,commit_date",
     "Commit nodes and relationships", "USED", "Required for Commit and Developer relationships"],
    ["Impact Graph", "files_clean.csv", "commit_sha,pr_number,file_name",
     "Commit-File relationships", "USED", "Required for impact propagation"],
    ["Impact Graph", "pull_requests_clean.csv", "pr_number,author",
     "PR nodes and PR-Commit relationships", "USED", "Required for PR graph structure"],
    ["Impact Graph", "issues_clean.csv", "issue_number",
     "Issue nodes", "USED", "Required for issue representation"],
    ["Impact Graph", "issue_pr_relationships.csv", "issue_number,pr_number",
     "Issue-PR relationships", "USED", "Only observed relationships are used"],

    # Developer-File
    ["Developer-File", "commits_clean.csv", "author,commit_date,commit_sha,pr_number",
     "Developer activity and first/last activity", "USED", "Builds developer-file relationships"],
    ["Developer-File", "files_clean.csv", "file_name,additions,deletions,changes,commit_sha,pr_number",
     "Commit count, additions, deletions, total changes, PR count", "USED",
     "Core relationship-strength features"],

    # Knowledge Concentration
    ["Knowledge Concentration", "developer-file relationships",
     "author,file_name,commit_count",
     "Unique developers, dominant share, concentration", "USED",
     "Measures ownership concentration and risk"],
    ["Knowledge Concentration", "developer-file relationships",
     "dominant_developer,dominant_developer_commit_count",
     "Dominant developer and commit count", "USED",
     "Supports concentration-risk evidence"],

    # Temporal
    ["Temporal Analysis", "commits_clean.csv", "commit_date,author,commit_sha",
     "Weekly commit activity and active developers", "USED",
     "Historical repository activity"],
    ["Temporal Analysis", "pull_requests_clean.csv",
     "created_at,updated_at,closed_at,merged_at,author,pr_number",
     "PR activity and backlog movement", "USED",
     "Temporal repository signals"],
    ["Temporal Analysis", "issues_clean.csv",
     "issue_number,created_at,updated_at,closed_at",
     "Issue activity and unresolved issues", "USED",
     "Temporal issue/backlog signals"],
    ["Temporal Analysis", "files_clean.csv",
     "commit_sha,file_name,additions,deletions,changes",
     "File activity and change volume", "USED",
     "Repository activity measurement"],
    ["Temporal Analysis", "developer-file relationships",
     "author,file_name",
     "Active/new developer-file relationships", "USED",
     "Detects relationship changes"],
    ["Temporal Analysis", "derived temporal data", "current_week + previous_weeks",
     "4-week rolling activity average", "USED",
     "Prevents future-data leakage"],

    # What-if
    ["What-If Simulation", "developer-file relationships",
     "author,file_name,commit_count",
     "Developer-unavailable impact", "USED",
     "Recalculates remaining developer ownership"],
    ["What-If Simulation", "developer-file relationships",
     "author,file_name",
     "Affected developers/files for file change", "USED",
     "Observed relationship evidence"],
    ["What-If Simulation", "pull_requests_clean.csv",
     "pr_number",
     "PR delay scenario", "USED",
     "Identifies affected PRs"],
    ["What-If Simulation", "issue_pr_relationships.csv",
     "issue_number,pr_number",
     "Affected issues", "USED",
     "Observed issue-PR evidence"],

    # Root Cause
    ["Root Cause Candidates", "commits_clean.csv",
     "commit_sha,author,commit_date,pr_number",
     "Candidate commit evidence", "USED",
     "Provides candidate events"],
    ["Root Cause Candidates", "files_clean.csv",
     "file_name,changes,additions,deletions",
     "Change magnitude and file frequency", "USED",
     "Candidate scoring evidence"],
    ["Root Cause Candidates", "pull_requests_clean.csv",
     "pr_number,title",
     "PR/title context", "USED",
     "Candidate context"],

    # Early Warning
    ["Early Warning", "temporal_features.csv",
     "activity_pattern_signal,activity_change_pct,unresolved_issues,new_dev_file_relationships",
     "Temporal warning signals", "USED",
     "Detects unusual repository activity"],
    ["Early Warning", "knowledge_concentration.csv",
     "concentration_risk_signal,dominant_developer_share",
     "Ownership concentration warnings", "USED",
     "Detects dependency concentration"],
    ["Early Warning", "developer_file_relationships.csv",
     "relationship_strength",
     "Strong developer-file dependency warning", "USED",
     "Detects high dependency relationships"],

    # Intentionally excluded
    ["Feature Audit", "issues_clean.csv", "title,body,author,comments_count,labels",
     "Text/metadata features", "EXCLUDED",
     "Not required for graph/temporal analysis; avoids duplicating NLP/ML work"],
    ["Feature Audit", "pull_requests_clean.csv", "body,draft,html_url",
     "PR text/presentation fields", "EXCLUDED",
     "Not required for graph/temporal calculations"],
    ["Feature Audit", "files_clean.csv", "status",
     "File status", "EXCLUDED",
     "Changes/additions/deletions already provide required change evidence"],
    ["Feature Audit", "commits_clean.csv", "commit_message",
     "Commit message NLP feature", "EXCLUDED",
     "Reserved for Member 1 NLP/ML analysis"],
]

df = pd.DataFrame(
    rows,
    columns=[
        "module",
        "source",
        "source_columns",
        "feature",
        "usage",
        "reason"
    ]
)

output = os.path.join(GRAPH_DIR, "feature_audit.csv")
df.to_csv(output, index=False)

print("=" * 60)
print("REPORESCUE - FEATURE AUDIT")
print("=" * 60)
print(f"Total audit rows : {len(df)}")
print(f"Used features    : {(df['usage'] == 'USED').sum()}")
print(f"Excluded fields  : {(df['usage'] == 'EXCLUDED').sum()}")
print(f"Output           : {output}")
print("\nFeature audit completed successfully.")