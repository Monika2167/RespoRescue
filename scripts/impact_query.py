import pandas as pd
from collections import defaultdict, deque


FILES_FILE = "data/cleaned/files_clean.csv"
COMMITS_FILE = "data/cleaned/commits_clean.csv"
ISSUE_PR_FILE = "data/issue_pr_relationships.csv"


def load_graph_data():
    files = pd.read_csv(FILES_FILE, dtype=str)
    commits = pd.read_csv(COMMITS_FILE, dtype=str)
    issue_pr = pd.read_csv(ISSUE_PR_FILE, dtype=str)

    files = files.dropna(
        subset=["commit_sha", "file_name", "pr_number"]
    )

    commits = commits.dropna(
        subset=["commit_sha", "pr_number", "author"]
    )

    issue_pr = issue_pr.dropna(
        subset=["issue_number", "pr_number"]
    )

    return files, commits, issue_pr


def build_graph(files, commits, issue_pr):

    graph = defaultdict(list)

    # PR <-> COMMIT
    for _, row in commits.iterrows():

        pr = f"PR:{row['pr_number']}"
        commit = f"COMMIT:{row['commit_sha']}"

        graph[pr].append(
            (commit, "PR_HAS_COMMIT")
        )

        graph[commit].append(
            (pr, "PR_HAS_COMMIT")
        )

    # COMMIT <-> FILE
    for _, row in files.iterrows():

        commit = f"COMMIT:{row['commit_sha']}"
        file = f"FILE:{row['file_name']}"

        graph[commit].append(
            (file, "COMMIT_MODIFIES_FILE")
        )

        graph[file].append(
            (commit, "COMMIT_MODIFIES_FILE")
        )

    # COMMIT <-> DEVELOPER
    for _, row in commits.iterrows():

        commit = f"COMMIT:{row['commit_sha']}"
        developer = f"DEVELOPER:{row['author']}"

        graph[commit].append(
            (developer, "DEVELOPER_AUTHORED_COMMIT")
        )

        graph[developer].append(
            (commit, "DEVELOPER_AUTHORED_COMMIT")
        )

    # PR <-> ISSUE
    for _, row in issue_pr.iterrows():

        pr = f"PR:{row['pr_number']}"
        issue = f"ISSUE:{row['issue_number']}"

        graph[pr].append(
            (issue, "ISSUE_HAS_PR")
        )

        graph[issue].append(
            (pr, "ISSUE_HAS_PR")
        )

    return graph


def find_impact(graph, entity_type, entity_id, max_depth=3):

    start = f"{entity_type.upper()}:{entity_id}"

    results = []

    queue = deque([
        (start, 0, [start])
    ])

    visited = {start}

    while queue:

        current, depth, path = queue.popleft()

        if depth >= max_depth:
            continue

        for related, relationship in graph.get(current, []):

            if related in visited:
                continue

            visited.add(related)

            results.append({
                "entity_type": entity_type.upper(),
                "entity_id": entity_id,
                "related_type": related.split(":", 1)[0],
                "related_id": related.split(":", 1)[1],
                "direct_or_indirect": (
                    "DIRECT"
                    if depth == 0
                    else "INDIRECT"
                ),
                "relationship": relationship,
                "impact_depth": depth + 1,
                "impact_path": " -> ".join(
                    path + [related]
                )
            })

            queue.append(
                (
                    related,
                    depth + 1,
                    path + [related]
                )
            )

    return pd.DataFrame(results)


def run_impact_query(
    entity_type,
    entity_id,
    max_depth=3
):

    files, commits, issue_pr = load_graph_data()

    graph = build_graph(
        files,
        commits,
        issue_pr
    )

    result = find_impact(
        graph,
        entity_type,
        entity_id,
        max_depth
    )

    return result


if __name__ == "__main__":

    print("=" * 60)
    print("IMPACT QUERY ENGINE")
    print("=" * 60)

    result = run_impact_query(
        entity_type="PR",
        entity_id="335918",
        max_depth=3
    )

    print("\nImpact results:")

    if result.empty:
        print("No connected entities found.")

    else:
        print(
            result.head(20).to_string(
                index=False
            )
        )

    output_file = (
        "data/graph/impact_query_results.csv"
    )

    result.to_csv(
        output_file,
        index=False
    )

    print("\nSaved:", output_file)
    print(
        "Total related entities:",
        len(result)
    )