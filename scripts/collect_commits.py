import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv

# ==========================================
# CONFIGURATION
# ==========================================

REPO = "microsoft/vscode"

PR_FILE = "data/pull_requests.csv"

# Temporary checkpoint files
CHECKPOINT_FILE = "data/commits_checkpoint.csv"
PROGRESS_FILE = "data/commits_progress.txt"

# Final output
FINAL_FILE = "data/commits.csv"

# ==========================================
# LOAD TOKEN
# ==========================================

load_dotenv()

token = os.getenv("GITHUB_TOKEN")

if not token:
    raise ValueError("GITHUB_TOKEN not found in .env")

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json"
}

# ==========================================
# LOAD PR DATA
# ==========================================

prs_df = pd.read_csv(PR_FILE)

pr_numbers = prs_df["pr_number"].astype(int).tolist()

print("Total PRs:", len(pr_numbers))

# ==========================================
# RESUME POSITION
# ==========================================

start_index = 0

if os.path.exists(PROGRESS_FILE):

    with open(PROGRESS_FILE, "r") as f:
        value = f.read().strip()

        if value:
            start_index = int(value)

print("Starting from PR index:", start_index)

# ==========================================
# LOAD EXISTING CHECKPOINT
# ==========================================

if os.path.exists(CHECKPOINT_FILE):

    commits_df = pd.read_csv(CHECKPOINT_FILE)

    commits = commits_df.to_dict("records")

    print(
        "Existing checkpoint commits:",
        len(commits)
    )

else:

    commits = []

    print("No checkpoint found. Starting fresh.")

# ==========================================
# SESSION
# ==========================================

session = requests.Session()

session.headers.update(headers)

# ==========================================
# FUNCTION: API REQUEST WITH RETRIES
# ==========================================

def get_with_retry(url, params):

    max_retries = 5

    for attempt in range(max_retries):

        try:

            response = session.get(
                url,
                params=params,
                timeout=30
            )

            # Success
            if response.status_code == 200:
                return response

            # Rate limit
            if response.status_code == 403:

                remaining = response.headers.get(
                    "X-RateLimit-Remaining"
                )

                reset = response.headers.get(
                    "X-RateLimit-Reset"
                )

                print(
                    f"\nRate limit response. "
                    f"Remaining: {remaining}"
                )

                if reset:

                    wait_time = max(
                        int(reset) - int(time.time()),
                        1
                    )

                    print(
                        f"Waiting {wait_time} seconds..."
                    )

                    time.sleep(wait_time + 5)

                    continue

            print(
                f"HTTP {response.status_code} "
                f"(attempt {attempt + 1}/{max_retries})"
            )

        except requests.exceptions.RequestException as e:

            print(
                f"Connection error "
                f"(attempt {attempt + 1}/{max_retries}): {e}"
            )

        wait_time = 2 ** attempt

        print(
            f"Retrying in {wait_time} seconds..."
        )

        time.sleep(wait_time)

    return None


# ==========================================
# MAIN COLLECTION
# ==========================================

for index in range(start_index, len(pr_numbers)):

    pr_number = pr_numbers[index]

    print(
        f"\n[{index + 1}/{len(pr_numbers)}] "
        f"Collecting PR #{pr_number}"
    )

    url = (
        f"https://api.github.com/repos/{REPO}"
        f"/pulls/{pr_number}/commits"
    )

    page = 1

    pr_success = True

    while True:

        params = {
            "per_page": 100,
            "page": page
        }

        response = get_with_retry(
            url,
            params
        )

        # If request completely failed
        if response is None:

            print(
                f"Could not collect PR #{pr_number}"
            )

            pr_success = False
            break

        data = response.json()

        if not data:
            break

        for commit in data:

            commit_info = commit.get(
                "commit",
                {}
            )

            author_info = commit.get(
                "author"
            )

            if author_info:

                author_name = author_info.get(
                    "login"
                )

            else:

                author_name = (
                    commit_info
                    .get("author", {})
                    .get("name")
                )

            commit_date = (
                commit_info
                .get("author", {})
                .get("date")
            )

            commits.append({
                "pr_number": pr_number,
                "commit_sha": commit.get("sha"),
                "commit_message": commit_info.get(
                    "message",
                    ""
                ),
                "author": author_name,
                "commit_date": commit_date
            })

        if len(data) < 100:
            break

        page += 1

    # ======================================
    # SAVE CHECKPOINT AFTER EACH PR
    # ======================================

    if pr_success:

        checkpoint_df = pd.DataFrame(
            commits
        )

        checkpoint_df.drop_duplicates(
            subset=["commit_sha"],
            inplace=True
        )

        checkpoint_df.to_csv(
            CHECKPOINT_FILE,
            index=False
        )


        with open(
            PROGRESS_FILE,
            "w"
        ) as f:

            f.write(
                str(index + 1)
            )

        print(
            f"Checkpoint saved. "
            f"Total commits: {len(checkpoint_df)}"
        )

    else:

        print(
            "Stopping safely. "
            "Restart script to resume."
        )

        break

    time.sleep(0.1)


# ==========================================
# FINAL SAVE
# ==========================================

if os.path.exists(CHECKPOINT_FILE):

    final_df = pd.read_csv(
        CHECKPOINT_FILE
    )

    final_df.drop_duplicates(
        subset=["commit_sha"],
        inplace=True
    )

    final_df.to_csv(
        FINAL_FILE,
        index=False
    )

    print("\n================================")
    print("COMMIT COLLECTION FINISHED")
    print("================================")

    print(
        "Total commits:",
        len(final_df)
    )

    print(
        "Unique PRs:",
        final_df["pr_number"].nunique()
    )

    print(
        "Earliest:",
        final_df["commit_date"].min()
    )

    print(
        "Latest:",
        final_df["commit_date"].max()
    )

    print(
        "\nFinal file:",
        FINAL_FILE
    )

else:

    print(
        "No checkpoint data available."
    )