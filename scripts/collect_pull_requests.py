import os
import json
import requests
import pandas as pd
from dotenv import load_dotenv

# ---------------------------------------
# Configuration
# ---------------------------------------

REPO = "microsoft/vscode"
TOTAL_PRS = 5000
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
# Create raw folder
# ---------------------------------------

os.makedirs("raw/pull_requests", exist_ok=True)

# ---------------------------------------
# GitHub API
# ---------------------------------------

url = f"https://api.github.com/repos/{REPO}/pulls"

pull_requests = []

page = 1

while len(pull_requests) < TOTAL_PRS:

    params = {
        "state": "all",
        "sort": "created",
        "direction": "desc",
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
        f"PRs collected: {len(pull_requests)}"
    )

    if response.status_code != 200:
        print(response.text)
        break

    data = response.json()

    if not data:
        print("No more PR data available.")
        break

    # Save raw response
    with open(
        f"raw/pull_requests/pull_requests_page_{page}.json",
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(data, f, indent=2)

    # ---------------------------------------
    # Extract PR information
    # ---------------------------------------

    for pr in data:

        pull_requests.append({
            "pr_id": pr["id"],
            "pr_number": pr["number"],
            "title": pr["title"],
            "body": pr["body"],
            "state": pr["state"],
            "created_at": pr["created_at"],
            "updated_at": pr["updated_at"],
            "closed_at": pr["closed_at"],
            "merged_at": pr["merged_at"],
            "author": pr["user"]["login"],
            "draft": pr["draft"],
            "html_url": pr["html_url"]
        })

        if len(pull_requests) >= TOTAL_PRS:
            break

    page += 1

# ---------------------------------------
# DataFrame
# ---------------------------------------

df = pd.DataFrame(pull_requests)

# Remove duplicates
df = df.drop_duplicates(
    subset=["pr_number"]
)

# Keep required number
df = df.head(TOTAL_PRS)

# ---------------------------------------
# Save
# ---------------------------------------

df.to_csv(
    "data/pull_requests.csv",
    index=False
)

# ---------------------------------------
# Summary
# ---------------------------------------

print("\n==============================")
print("PR DATA COLLECTION COMPLETE")
print("==============================")

print("Total PRs:", len(df))

print(
    "Earliest PR:",
    df["created_at"].min()
)

print(
    "Latest PR:",
    df["created_at"].max()
)

print(
    "Date range:",
    pd.to_datetime(df["created_at"]).max()
    - pd.to_datetime(df["created_at"]).min()
)

print("\nSaved to:")
print("data/pull_requests.csv")

print("==============================")