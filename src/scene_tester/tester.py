from src.scene_tester.validator import validate_scenes
from src.scene_tester.reviewer import review_scenes


def test_scene_plan(original_script: str, scene_plan):

    print("\n========== SCENE QUALITY TEST ==========\n")

    # 1. Run objective Python validation
    print("Running Python validation...")

    python_issues = validate_scenes(
        original_script,
        scene_plan
    )

    # 2. Run AI-based creative review
    print("Running AI scene review...")

    ai_review = review_scenes(
        original_script,
        scene_plan.model_dump()
    )

    # 3. Combine both results
    critical_issues = [
    issue for issue in ai_review.issues
    if issue.severity == "CRITICAL"
    ]

    passed = (
        len(python_issues) == 0
        and ai_review.passed
        and len(critical_issues) == 0
        )

    # 4. Display Python issues
    print("\n--- PYTHON VALIDATION ---")

    if python_issues:
        for issue in python_issues:
            print("FAILED:", issue)
    else:
        print("All objective checks passed.")

    # 5. Display AI review
    print("\n--- AI REVIEW ---")

    print("AI Review Passed:", ai_review.passed)

    for issue in ai_review.issues:
        print(f"\nScene {issue.scene_number}")
        print("Severity:", issue.severity)
        print("Problem:", issue.issue)
        print("Explanation:", issue.explanation)
        print("Suggested Fix:", issue.suggested_fix)

    print("\nOverall Feedback:", ai_review.overall_feedback)

    # 6. Final decision
    print("\n========== FINAL RESULT ==========")

    if passed:
        print("APPROVED: Scene plan passed all checks.")
    else:
        print("REJECTED: Scene plan needs improvement.")

    return {
        "passed": passed,
        "python_issues": python_issues,
        "ai_review": ai_review
    }