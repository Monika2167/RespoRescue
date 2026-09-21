import os
import pandas as pd


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATA_DIR = os.path.join(BASE_DIR, "data")
GRAPH_DIR = os.path.join(DATA_DIR, "graph")

TEMPORAL_PATH = os.path.join(
    GRAPH_DIR,
     "temporal_features.csv"
)

KNOWLEDGE_PATH = os.path.join(
    GRAPH_DIR,
    "knowledge_concentration.csv"
)

DEVELOPER_FILE_PATH = os.path.join(
    GRAPH_DIR,
    "developer_file_relationships.csv"
)

OUTPUT_PATH = os.path.join(
    GRAPH_DIR,
    "early_warning_signals.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    print("Loading early-warning evidence...")

    temporal = pd.read_csv(
        TEMPORAL_PATH
    )

    knowledge = pd.read_csv(
        KNOWLEDGE_PATH
    )

    developer_file = pd.read_csv(
        DEVELOPER_FILE_PATH
    )

    print(
        "Temporal rows:",
        len(temporal)
    )

    print(
        "Knowledge concentration rows:",
        len(knowledge)
    )

    print(
        "Developer-file rows:",
        len(developer_file)
    )

    return (
        temporal,
        knowledge,
        developer_file
    )


# ============================================================
# TEMPORAL WARNING SIGNALS
# ============================================================

def temporal_signals(temporal):

    print("\nAnalyzing temporal warning signals...")

    rows = []

    for _, row in temporal.iterrows():

        warnings = []

        # --------------------------------------------
        # Activity pattern
        # --------------------------------------------

        activity_signal = str(
            row.get(
                "activity_pattern_signal",
                "LOW"
            )
        )

        if activity_signal.upper() in [
            "HIGH",
            "MEDIUM"
        ]:

            warnings.append(
                "UNUSUAL_ACTIVITY"
            )

        # --------------------------------------------
        # Repository activity change
        # --------------------------------------------

        activity_change = row.get(
            "activity_change_pct",
            0
        )

        try:
            activity_change = float(
                activity_change
            )
        except:
            activity_change = 0

        if activity_change >= 50:

            warnings.append(
                "ACTIVITY_SPIKE"
            )

        # --------------------------------------------
        # Backlog
        # --------------------------------------------

        unresolved = row.get(
            "unresolved_issues",
            0
        )

        try:
            unresolved = float(
                unresolved
            )
        except:
            unresolved = 0

        if unresolved >= 100:

            warnings.append(
                "HIGH_UNRESOLVED_BACKLOG"
            )

        # --------------------------------------------
        # Developer-file changes
        # --------------------------------------------

        new_relationships = row.get(
            "new_developer_file_relationships",
            0
        )

        try:
            new_relationships = float(
                new_relationships
            )
        except:
            new_relationships = 0

        if new_relationships >= 100:

            warnings.append(
                "RELATIONSHIP_GROWTH"
            )

        # --------------------------------------------
        # Warning level
        # --------------------------------------------

        if len(warnings) >= 3:

            warning_level = "HIGH"

        elif len(warnings) >= 1:

            warning_level = "MEDIUM"

        else:

            warning_level = "LOW"

        rows.append({

            "signal_type":
                "TEMPORAL",

            "period":
                row.get(
                    "week",
                    row.get(
                        "period",
                        ""
                    )
                ),

            "warning_level":
                warning_level,

            "warning_count":
                len(warnings),

            "warning_signals":
                ";".join(warnings),

            "evidence":
                "Temporal repository activity analysis."

        })

    return rows


# ============================================================
# KNOWLEDGE CONCENTRATION WARNINGS
# ============================================================

def concentration_signals(knowledge):

    print(
        "\nAnalyzing knowledge concentration..."
    )

    rows = []

    for _, row in knowledge.iterrows():

        risk = str(
            row.get(
                "concentration_risk_signal",
                "LOW"
            )
        ).upper()

        if risk == "HIGH":

            warning_level = "HIGH"

            signal = (
                "HIGH_DEVELOPER_CONCENTRATION"
            )

        elif risk == "MEDIUM":

            warning_level = "MEDIUM"

            signal = (
                "MEDIUM_DEVELOPER_CONCENTRATION"
            )

        else:

            warning_level = "LOW"

            signal = ""

        if warning_level != "LOW":

            rows.append({

                "signal_type":
                    "KNOWLEDGE_CONCENTRATION",

                "period":
                    "",

                "warning_level":
                    warning_level,

                "warning_count":
                    1,

                "warning_signals":
                    signal,

                "affected_file":
                    row.get(
                        "file_name",
                        ""
                    ),

                "affected_developer":
                    row.get(
                        "dominant_developer",
                        ""
                    ),

                "evidence":
                    (
                        "Developer contribution "
                        "concentration in a repository file."
                    )
            })

    return rows


# ============================================================
# DEVELOPER-FILE WARNING SIGNALS
# ============================================================

def relationship_signals(developer_file):

    print(
        "\nAnalyzing developer-file relationships..."
    )

    rows = []

    # Relationship strength threshold
    strength_values = pd.to_numeric(
        developer_file[
            "relationship_strength"
        ],
        errors="coerce"
    ).fillna(0)

    threshold = strength_values.quantile(
        0.95
    )

    for _, row in developer_file.iterrows():

        strength = pd.to_numeric(
            row.get(
                "relationship_strength",
                0
            ),
            errors="coerce"
        )

        if strength >= threshold:

            rows.append({

                "signal_type":
                    "DEVELOPER_FILE",

                "period":
                    "",

                "warning_level":
                    "MEDIUM",

                "warning_count":
                    1,

                "warning_signals":
                    "STRONG_DEVELOPER_FILE_DEPENDENCY",

                "affected_file":
                    row.get(
                        "file_name",
                        ""
                    ),

                "affected_developer":
                    row.get(
                        "author",
                        ""
                    ),

                "evidence":
                    (
                        "Developer-file relationship "
                        "is among the strongest observed "
                        "relationships."
                    )
            })

    return rows


# ============================================================
# SAVE RESULTS
# ============================================================

def save_results(rows):

    result = pd.DataFrame(
        rows
    )

    os.makedirs(
        GRAPH_DIR,
        exist_ok=True
    )

    result.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print(
        "\nEarly-warning analysis completed."
    )

    print(
        "Total warning signals:",
        len(result)
    )

    print(
        "Output:",
        OUTPUT_PATH
    )

    if len(result) > 0:

        print(
            "\nWarning levels:"
        )

        print(
            result[
                "warning_level"
            ].value_counts()
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print(
        "REPORESCUE - EARLY WARNING SYSTEM"
    )
    print("=" * 60)

    (
        temporal,
        knowledge,
        developer_file
    ) = load_data()

    rows = []

    rows.extend(
        temporal_signals(
            temporal
        )
    )

    rows.extend(
        concentration_signals(
            knowledge
        )
    )

    rows.extend(
        relationship_signals(
            developer_file
        )
    )

    save_results(
        rows
    )


if __name__ == "__main__":
    main()