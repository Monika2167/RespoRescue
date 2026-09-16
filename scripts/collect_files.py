import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv


# ============================================================
# LOAD .ENV
# ============================================================

load_dotenv(dotenv_path="scripts/.env")


# ============================================================
# CONFIGURATION
# ============================================================

REPO = "microsoft/vscode"

COMMITS_FILE = "data/commits.csv"
OUTPUT_FILE = "data/files.csv"
PROGRESS_FILE = "data/files_progress.txt"


# ============================================================
# GITHUB TOKEN
# ============================================================

TOKEN = os.getenv("GITHUB_TOKEN")

if not TOKEN:
    print("ERROR: GITHUB_TOKEN was not found.")
    print("Expected location:")
    print("scripts/.env")
    raise SystemExit(1)


HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28"
}


# ============================================================
# SESSION
# ============================================================

session = requests.Session()
session.headers.update(HEADERS)


# ============================================================
# CHECK GITHUB AUTHENTICATION
# ============================================================

def check_authentication():

    url = "https://api.github.com/user"

    try:

        response = session.get(
            url,
            timeout=30
        )

        if response.status_code == 200:

            username = response.json().get(
                "login",
                "unknown"
            )

            print()
            print("GitHub authentication: SUCCESS")
            print(f"Authenticated as: {username}")
            print()

            return True

        elif response.status_code == 401:

            print()
            print("ERROR: GitHub authentication failed.")
            print("The token is invalid or expired.")
            print()

            return False

        else:

            print(
                f"Authentication check failed: "
                f"HTTP {response.status_code}"
            )

            return False

    except requests.RequestException as e:

        print(
            f"Authentication check failed: {e}"
        )

        return False


# ============================================================
# LOAD COMMITS
# ============================================================

def load_commits():

    if not os.path.exists(COMMITS_FILE):

        print(
            f"ERROR: {COMMITS_FILE} not found."
        )

        raise SystemExit(1)

    df = pd.read_csv(
        COMMITS_FILE
    )

    if "commit_sha" not in df.columns:

        print(
            "ERROR: commit_sha column missing."
        )

        raise SystemExit(1)

    return df


# ============================================================
# GET FILES FOR ONE COMMIT
# ============================================================

def get_files(commit_sha):

    url = (
        f"https://api.github.com/repos/"
        f"{REPO}/commits/{commit_sha}"
    )

    for attempt in range(5):

        try:

            response = session.get(
                url,
                timeout=60
            )

            # SUCCESS
            if response.status_code == 200:

                data = response.json()

                return data.get(
                    "files",
                    []
                )


            # RATE LIMIT
            if response.status_code == 403:

                remaining = response.headers.get(
                    "X-RateLimit-Remaining"
                )

                reset_time = response.headers.get(
                    "X-RateLimit-Reset"
                )

                print()
                print(
                    "GitHub rate limit encountered."
                )

                if remaining == "0" and reset_time:

                    wait_seconds = (
                        max(
                            int(reset_time)
                            - int(time.time()),
                            0
                        )
                        + 10
                    )

                    print(
                        f"Waiting {wait_seconds} seconds..."
                    )

                    time.sleep(
                        wait_seconds
                    )

                else:

                    time.sleep(30)

                continue


            # NOT FOUND
            if response.status_code == 404:

                print(
                    f"Commit not found: {commit_sha}"
                )

                return []


            # AUTHENTICATION ERROR
            if response.status_code == 401:

                print()
                print(
                    "ERROR: HTTP 401."
                )
                print(
                    "GitHub authentication failed."
                )
                print()

                return None


            print(
                f"HTTP {response.status_code} "
                f"for commit {commit_sha}"
            )

        except requests.RequestException as e:

            print(
                f"Network error "
                f"(attempt {attempt + 1}/5): {e}"
            )

        time.sleep(
            2 ** attempt
        )

    return None


# ============================================================
# LOAD PROGRESS
# ============================================================

def load_progress():

    if not os.path.exists(
        PROGRESS_FILE
    ):

        return 0

    try:

        with open(
            PROGRESS_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            value = f.read().strip()

        if value:

            return int(value)

    except Exception:

        pass

    return 0


# ============================================================
# SAVE PROGRESS
# ============================================================

def save_progress(index):

    try:

        with open(
            PROGRESS_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                str(index)
            )

        return True

    except PermissionError:

        print(
            "WARNING: Could not save "
            "progress file."
        )

        return False


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 40)
    print("FILES COLLECTION")
    print("=" * 40)

    # --------------------------------------------------------
    # AUTHENTICATION
    # --------------------------------------------------------

    if not check_authentication():

        raise SystemExit(1)

    # --------------------------------------------------------
    # LOAD COMMITS
    # --------------------------------------------------------

    commits_df = load_commits()

    total = len(
        commits_df
    )

    print(
        f"Total commits: {total}"
    )

    # --------------------------------------------------------
    # LOAD EXISTING FILE DATA
    # --------------------------------------------------------

    if os.path.exists(
        OUTPUT_FILE
    ):

        files_df = pd.read_csv(
            OUTPUT_FILE
        )

        print(
            f"Existing file records: "
            f"{len(files_df)}"
        )

    else:

        files_df = pd.DataFrame(
            columns=[
                "commit_sha",
                "pr_number",
                "file_name",
                "status",
                "additions",
                "deletions",
                "changes"
            ]
        )

    existing_shas = set(
        files_df["commit_sha"]
        .astype(str)
    )

    # --------------------------------------------------------
    # RESUME
    # --------------------------------------------------------

    start_index = load_progress()

    print(
        f"Starting from commit index: "
        f"{start_index}"
    )

    print()

    # --------------------------------------------------------
    # PROCESS COMMITS
    # --------------------------------------------------------

    for index in range(
        start_index,
        total
    ):

        row = commits_df.iloc[
            index
        ]

        sha = str(
            row["commit_sha"]
        )

        pr_number = row.get(
            "pr_number",
            None
        )

        # Skip already collected
        if sha in existing_shas:

            save_progress(
                index + 1
            )

            continue

        print(
            f"[{index + 1}/{total}] "
            f"Commit: {sha[:12]}"
        )

        files = get_files(
            sha
        )

        # Failure
        if files is None:

            print()
            print(
                "Collection stopped safely."
            )

            print(
                f"Resume from index: {index}"
            )

            break

        # ----------------------------------------------------
        # CREATE FILE RECORDS
        # ----------------------------------------------------

        new_rows = []

        for file in files:

            new_rows.append({

                "commit_sha": sha,

                "pr_number": pr_number,

                "file_name": file.get(
                    "filename"
                ),

                "status": file.get(
                    "status"
                ),

                "additions": file.get(
                    "additions",
                    0
                ),

                "deletions": file.get(
                    "deletions",
                    0
                ),

                "changes": file.get(
                    "changes",
                    0
                )
            })

        # ----------------------------------------------------
        # SAVE FILE DATA
        # ----------------------------------------------------

        if new_rows:

            new_df = pd.DataFrame(
                new_rows
            )

            files_df = pd.concat(
                [
                    files_df,
                    new_df
                ],
                ignore_index=True
            )

            try:

                files_df.to_csv(
                    OUTPUT_FILE,
                    index=False
                )

            except PermissionError:

                print()
                print(
                    "ERROR: files.csv is locked."
                )

                print(
                    "Close files.csv and try again."
                )

                break

        existing_shas.add(
            sha
        )

        # ----------------------------------------------------
        # SAVE PROGRESS
        # ----------------------------------------------------

        save_progress(
            index + 1
        )

    # ========================================================
    # FINAL STATUS
    # ========================================================

    print()
    print("=" * 40)
    print("FILES COLLECTION STATUS")
    print("=" * 40)

    if os.path.exists(
        OUTPUT_FILE
    ):

        final_df = pd.read_csv(
            OUTPUT_FILE
        )

        print(
            f"File records: "
            f"{len(final_df)}"
        )

        print(
            f"Unique commits with files: "
            f"{final_df['commit_sha'].nunique()}"
        )

        print(
            f"Unique PRs represented: "
            f"{final_df['pr_number'].nunique()}"
        )

    current_progress = load_progress()

    print(
        f"Progress: "
        f"{current_progress}/{total}"
    )

    if current_progress >= total:

        print()
        print(
            "FILES COLLECTION FINISHED SUCCESSFULLY"
        )

    else:

        print()
        print(
            "FILES COLLECTION PAUSED / STOPPED"
        )

        print(
            "Run again to resume."
        )

    print("=" * 40)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()