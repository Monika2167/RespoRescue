import pandas as pd
from pathlib import Path
from collections import defaultdict
from itertools import combinations

# -----------------------------
# Paths
# -----------------------------
BASE_DIR = Path(__file__).resolve().parents[1]

FILES_FILE = BASE_DIR / "data" / "cleaned" / "files_clean.csv"
OUTPUT_DIR = BASE_DIR / "data" / "graph"
OUTPUT_FILE = OUTPUT_DIR / "impact_analysis.csv"

# -----------------------------
# Load data
# -----------------------------
files = pd.read_csv(FILES_FILE)

print("Dataset loaded successfully.")
print("File changes:", len(files))

files = files.dropna(subset=["commit_sha", "file_name"])

# -----------------------------
# Create commit -> unique files
# -----------------------------
commit_files = (
    files.groupby("commit_sha")["file_name"]
    .apply(lambda x: list(set(x)))
)

print("Commits found:", len(commit_files))

# -----------------------------
# Count historical co-changes
# -----------------------------
cochange_counts = defaultdict(int)

processed = 0

for commit_sha, file_list in commit_files.items():

    # Skip single-file commits
    if len(file_list) < 2:
        continue

    # Safety limit for very large commits
    # Prevents huge pair generation
    if len(file_list) > 100:
        continue

    for file_a, file_b in combinations(sorted(file_list), 2):
        cochange_counts[(file_a, file_b)] += 1

    processed += 1

    if processed % 1000 == 0:
        print("Processed commits:", processed)

# -----------------------------
# Convert to DataFrame
# -----------------------------
records = []

for (source_file, target_file), frequency in cochange_counts.items():

    records.append({
        "source_file": source_file,
        "target_file": target_file,
        "cochange_frequency": frequency,
        "impact_weight": frequency
    })

impact_analysis = pd.DataFrame(records)

# -----------------------------
# Sort strongest relationships
# -----------------------------
if not impact_analysis.empty:
    impact_analysis = impact_analysis.sort_values(
        "impact_weight",
        ascending=False
    )

# -----------------------------
# Save output
# -----------------------------
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

impact_analysis.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nImpact propagation analysis completed!")

print(
    "Historical co-change relationships:",
    len(impact_analysis)
)

print("\nOutput file:")
print(OUTPUT_FILE)

print("\nTop co-change relationships:")

if not impact_analysis.empty:
    print(
        impact_analysis.head(10).to_string(index=False)
    )
else:
    print("No co-change relationships found.")