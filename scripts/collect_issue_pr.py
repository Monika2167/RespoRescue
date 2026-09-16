import os
import requests
import pandas as pd
import time
from dotenv import load_dotenv

# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "data")
ENV_PATH = os.path.join(BASE_DIR, "scripts", ".env")

ISSUES_FILE = os.path.join(DATA_DIR, "issues.csv")
OUTPUT_FILE = os.path.join(DATA_DIR, "issue_pr_relationships.csv")
CHECKPOINT_FILE = os.path.join(DATA_DIR, "issue_pr_progress.csv")

# ============================================================
# LOAD TOKEN
# ============================================================

load_dotenv(ENV_PATH)

token = os.getenv("GITHUB_TOKEN")

if not token:
    raise ValueError("GITHUB_TOKEN not found")

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json"
}

# ============================================================
# LOAD ISSUES
# ============================================================

issues_df = pd.read_csv(ISSUES_FILE)

print("Total issues:", len(issues_df))

# ============================================================
# LOAD CHECKPOINT
# ============================================================

relationships = []
processed_issues = set()

if os.path.exists(CHECKPOINT_FILE):

    checkpoint_df = pd.read_csv(CHECKPOINT_FILE)

    if not checkpoint_df.empty:

        processed_issues = set(
            checkpoint_df["issue_number"]
            .astype(int)
        )

        relationship_columns = [
            "issue_number",
            "pr_number"
        ]

        if all(
            col in checkpoint_df.columns
            for col in relationship_columns
        ):

            old_relationships = checkpoint_df[
                relationship_columns
            ].dropna()

            relationships = (
                old_relationships
                .to_dict("records")
            )

        print(
            "Resuming from checkpoint."
        )

        print(
            "Already processed:",
            len(processed_issues)
        )

# ============================================================
# PROCESS ISSUES
# ============================================================

for index, issue in issues_df.iterrows():

    issue_number = int(issue["issue_number"])

    if issue_number in processed_issues:
        continue

    print(
        f"Checking Issue #{issue_number} "
        f"({index + 1}/{len(issues_df)})..."
    )

    url = (
        f"https://api.github.com/repos/microsoft/vscode/"
        f"issues/{issue_number}/timeline"
    )

    page = 1

    while True:

        response = requests.get(
            url,
            headers=headers,
            params={
                "per_page": 100,
                "page": page
            },
            timeout=30
        )

        # ----------------------------------------------------
        # RATE LIMIT
        # ----------------------------------------------------

        if response.status_code == 403:

            print("\n⚠️ GitHub rate limit reached.")
            print("Progress has already been saved.")
            print("Run the script again later.")

            raise SystemExit

        # ----------------------------------------------------
        # OTHER ERROR
        # ----------------------------------------------------

        if response.status_code != 200:

            print(
                "Error:",
                response.status_code
            )

            break

        timeline = response.json()

        # ----------------------------------------------------
        # FIND ISSUE → PR
        # ----------------------------------------------------

        for event in timeline:

            if event.get("event") != "cross-referenced":
                continue

            source = event.get("source", {})

            issue_data = source.get("issue", {})

            if "pull_request" in issue_data:

                pr_number = issue_data.get("number")

                if pr_number:

                    relationships.append({
                        "issue_number": issue_number,
                        "pr_number": pr_number
                    })

        # ----------------------------------------------------
        # PAGINATION
        # ----------------------------------------------------

        if len(timeline) < 100:
            break

        page += 1

    # --------------------------------------------------------
    # MARK ISSUE PROCESSED
    # --------------------------------------------------------

    processed_issues.add(issue_number)

    # --------------------------------------------------------
    # SAVE CHECKPOINT
    # --------------------------------------------------------

    checkpoint_df = pd.DataFrame({
        "issue_number": list(processed_issues)
    })

    checkpoint_df.to_csv(
        CHECKPOINT_FILE,
        index=False
    )

    # Save relationships separately
    relationship_df = pd.DataFrame(
        relationships,
        columns=[
            "issue_number",
            "pr_number"
        ]
    )

    if not relationship_df.empty:

        relationship_df = relationship_df.drop_duplicates(
            subset=[
                "issue_number",
                "pr_number"
            ]
        )

    relationship_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    time.sleep(0.1)

# ============================================================
# FINAL SUMMARY
# ============================================================

df = pd.DataFrame(
    relationships,
    columns=[
        "issue_number",
        "pr_number"
    ]
)

if not df.empty:

    df = df.drop_duplicates(
        subset=[
            "issue_number",
            "pr_number"
        ]
    )

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n========================================")
print("ISSUE → PR COLLECTION COMPLETED")
print("========================================")

print(
    "Issues processed:",
    len(processed_issues)
)

print(
    "Relationships found:",
    len(df)
)

print(
    "Unique issues linked:",
    df["issue_number"].nunique()
    if not df.empty else 0
)

print(
    "Unique PRs linked:",
    df["pr_number"].nunique()
    if not df.empty else 0
)

print(
    "Saved to:",
    OUTPUT_FILE
)

print("========================================")