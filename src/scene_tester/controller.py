from src.scene_planner.planner import generate_scene_plan
from src.scene_tester.tester import test_scene_plan


MAX_ATTEMPTS = 3


def create_approved_scene_plan(original_script: str):

    feedback = ""

    for attempt in range(1, MAX_ATTEMPTS + 1):

        print(f"\n========== ATTEMPT {attempt} ==========\n")

        # 1. Generate storyboard
        print("Generating scene plan...")

        scene_plan = generate_scene_plan(
            original_script,
            feedback
        )

        # 2. Test storyboard
        result = test_scene_plan(
            original_script,
            scene_plan
        )

        # 3. Check whether it passed
        if result["passed"]:

            print("\nSUCCESS: Scene plan approved!")

            return scene_plan

        # 4. Prepare feedback for regeneration
        print("\nScene plan rejected. Preparing feedback...")

        feedback_parts = []

        for issue in result["python_issues"]:
            feedback_parts.append(
                f"Python validation issue: {issue}"
            )

        for issue in result["ai_review"].issues:
            if issue.severity == "CRITICAL":
                feedback_parts.append(f"Scene {issue.scene_number}: "
                                      f"{issue.issue}. "
                                      f"{issue.explanation}. "
                                      f"Suggested fix: {issue.suggested_fix}" )

        feedback = "\n".join(feedback_parts)

    print("\nMaximum attempts reached.")
    print("Human review required.")

    return None