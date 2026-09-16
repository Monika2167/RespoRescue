import pandas as pd
import matplotlib.pyplot as plt

# Load cleaned dataset
df = pd.read_csv("data/processed/issues_clean.csv")

print("\n==============================")
print("EDA - ISSUE ACTIVITY ANALYSIS")
print("==============================")

# -------------------------------
# 1. Issue State
# -------------------------------
print("\n1. Issue State Distribution:")
print(df["state"].value_counts())

print("\nIssue State Percentage:")
print(
    (df["state"].value_counts(normalize=True) * 100).round(2)
)

# -------------------------------
# 2. Comments
# -------------------------------
print("\n2. Comments Statistics:")
print(df["comments_count"].describe())

print("\nComment Frequency:")
print(df["comments_count"].value_counts().sort_index())

# -------------------------------
# 3. Labels
# -------------------------------
labels = (
    df["labels"]
    .fillna("")
    .astype(str)
    .str.split(",")
    .explode()
    .str.strip()
)

labels = labels[labels != ""]

print("\n3. Number of Unique Labels:")
print(labels.nunique())

print("\nTop 15 Labels:")
print(labels.value_counts().head(15))

# -------------------------------
# 4. Issues with / without labels
# -------------------------------
no_labels = df["labels"].fillna("").str.strip().eq("").sum()
with_labels = len(df) - no_labels

print("\n4. Issues With Labels:", with_labels)
print("5. Issues Without Labels:", no_labels)

# -------------------------------
# 5. Graph - State
# -------------------------------
plt.figure(figsize=(6, 4))

df["state"].value_counts().plot(kind="bar")

plt.title("Issue State Distribution")
plt.xlabel("Issue State")
plt.ylabel("Number of Issues")
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()

# -------------------------------
# 6. Graph - Comments
# -------------------------------
plt.figure(figsize=(7, 4))

df["comments_count"].value_counts().sort_index().plot(kind="bar")

plt.title("Comments per Issue")
plt.xlabel("Number of Comments")
plt.ylabel("Number of Issues")
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()

# -------------------------------
# 7. Graph - Top Labels
# -------------------------------
plt.figure(figsize=(10, 5))

labels.value_counts().head(15).plot(kind="bar")

plt.title("Top 15 Issue Labels")
plt.xlabel("Label")
plt.ylabel("Number of Issues")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.show()