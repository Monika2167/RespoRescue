import os
import json
import requests
import pandas as pd
from dotenv import load_dotenv

# ---------------------------------------
# Configuration
# ---------------------------------------

REPO = "microsoft/vscode"
TOTAL_ISSUES = 5000
PER_PAGE = 100

# ---------------------------------------
# Load GitHub token
# ---------------------------------------

load_dotenv()

token = os.getenv("GITHUB_TOKEN")

if not token:
    raise ValueError("GITHUB_TOKEN not found in .env file")

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json"
}

# ---------------------------------------
# Create raw data folder
# ---------------------------------------

os.makedirs("raw/issues", exist_ok=True)

# ---------------------------------------
# GitHub API
# ---------------------------------------

url = f"https://api.github.com/repos/{REPO}/issues"

issues = []

page = 1

while len(issues) < TOTAL_ISSUES:

    params = {
        "state": "all",
        "per_page": PER_PAGE,
        "page": page
    }

    response = requests.get(
        url,
        headers=headers,
        params=params
    )

    print(
        f"Page {page} | "
        f"Status: {response.status_code} | "
        f"Issues collected: {len(issues)}"
    )

    if response.status_code != 200:
        print(response.text)
        break

    data = response.json()

    if not data:
        print("No more data available.")
        break

    # Save raw API response
    with open(
        f"raw/issues/issues_page_{page}.json",
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(data, f, indent=2)

    # ---------------------------------------
    # Extract ONLY actual issues
    # ---------------------------------------

    for issue in data:

        # GitHub represents PRs with a "pull_request" field
        if "pull_request" in issue:
            continue

        labels = [
            label["name"]
            for label in issue.get("labels", [])
        ]

        issues.append({
            "issue_number": issue["number"],
            "title": issue["title"],
            "body": issue["body"],
            "state": issue["state"],
            "created_at": issue["created_at"],
            "updated_at": issue["updated_at"],
            "closed_at": issue["closed_at"],
            "author": issue["user"]["login"],
            "comments_count": issue["comments"],
            "labels": ", ".join(labels)
        })

        if len(issues) >= TOTAL_ISSUES:
            break

    page += 1

# ---------------------------------------
# Create dataframe
# ---------------------------------------

df = pd.DataFrame(issues)

# Remove duplicates
df = df.drop_duplicates(
    subset=["issue_number"]
)

# Keep required number
df = df.head(TOTAL_ISSUES)

# ---------------------------------------
# Save dataset
# ---------------------------------------

df.to_csv(
    "data/issues.csv",
    index=False
)

# ---------------------------------------
# Summary
# ---------------------------------------

print("\n==============================")
print("ISSUE DATA COLLECTION COMPLETE")
print("==============================")

print("Total issues:", len(df))

print(
    "Earliest issue:",
    df["created_at"].min()
)

print(
    "Latest issue:",
    df["created_at"].max()
)

print(
    "Date range:",
    pd.to_datetime(df["created_at"]).max()
    - pd.to_datetime(df["created_at"]).min()
)

print("\nColumns:")
print(df.columns.tolist())

print("\nSaved to:")
print("data/issues.csv")

print("==============================")