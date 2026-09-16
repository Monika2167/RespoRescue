from predict_pr import predict_pr


# ============================================================
# REPORESCUE - PREDICTION VALIDATION TEST
# ============================================================

test_prs = [
    333333,
    333999,
    326789
]


print("=" * 60)
print("REPORESCUE PREDICTION VALIDATION")
print("=" * 60)


for pr_number in test_prs:

    print(
        f"\nTesting PR #{pr_number}..."
    )

    result = predict_pr(
        pr_number
    )


    if not result["success"]:

        print(
            f"❌ {result['error']}"
        )

        continue


    print(
        f"✓ Probability: "
        f"{result['probability_percent']:.2f}%"
    )

    print(
        f"✓ Prediction: "
        f"{result['prediction']}"
    )

    print(
        f"✓ Threshold: "
        f"{result['threshold']}"
    )

    print(
        f"✓ Semantic signal: "
        f"{result['semantic_signal']}"
    )

    print(
        "✓ Top evidence:"
    )

    for evidence in result[
        "top_evidence"
    ][:3]:

        print(
            f"   - {evidence['explanation']}"
        )


print(
    "\n" + "=" * 60
)

print(
    "VALIDATION TEST COMPLETED"
)

print(
    "=" * 60
)