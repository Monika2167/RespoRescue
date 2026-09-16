import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("GITHUB_TOKEN")

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json"
}

sha = "229facda6b80e0c6415a97dccb1455749b03e519"

url = f"https://api.github.com/repos/microsoft/vscode/commits/{sha}"

response = requests.get(url, headers=headers)

print("Status code:", response.status_code)

if response.status_code == 200:

    data = response.json()

    files = data.get("files", [])

    print("Files returned by GitHub:", len(files))

    print("\nCommit message:")
    print(data["commit"]["message"])

    print("\nCommit SHA:")
    print(data["sha"])

    print("\nAPI response keys:")
    print(list(data.keys()))

    if len(files) == 300:
        print("\n⚠️ GitHub returned exactly 300 files.")
        print("This commit may be affected by the API file limit.")

    else:
        print("\n✅ GitHub returned fewer than 300 files.")

else:
    print("Error:", response.text)