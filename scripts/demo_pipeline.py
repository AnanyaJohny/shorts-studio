from src.script_generator.generator import generate_script
from src.scene_planner.planner import generate_scene_plan
from src.scene_tester.validator import validate_scenes
from src.scene_tester.reviewer import review_scenes
from src.project_manager import create_project


def run_pipeline_test():

    print("\n========== SHORTS STUDIO PIPELINE TEST ==========\n")

    topic = "Why do we replay awkward conversations in our heads?"

    # STEP 1: Generate script
    print("STEP 1: Generating script...")

    script = generate_script(topic)

    print("\nGenerated Script:")
    print(script.full_script)

    # STEP 2: Generate storyboard
    print("\nSTEP 2: Generating storyboard...")

    scene_plan = generate_scene_plan(script.full_script)

    for scene in scene_plan.scenes:
        print(f"\nScene {scene.scene_number}")
        print(f"Narration: {scene.narration}")
        print(f"Visual: {scene.visual_description}")

    # STEP 3: Python validation
    print("\nSTEP 3: Running Python validation...")

    python_issues = validate_scenes(
        script.full_script,
        scene_plan
    )

    if python_issues:
        print("\nPYTHON VALIDATION: FAILED")

        for issue in python_issues:
            print(f"- {issue}")

    else:
        print("\nPYTHON VALIDATION: PASSED")

    # STEP 4: AI visual review
    print("\nSTEP 4: Running AI visual review...")

    ai_review = review_scenes(
        script.full_script,
        scene_plan.model_dump()
    )

    print(f"\nAI REVIEW PASSED: {ai_review.passed}")

    for issue in ai_review.issues:
        print(f"\nScene: {issue.scene_number}")
        print(f"Severity: {issue.severity}")
        print(f"Problem: {issue.issue}")
        print(f"Explanation: {issue.explanation}")
        print(f"Suggested fix: {issue.suggested_fix}")

    # STEP 5: Final result
    print("\n========== FINAL RESULT ==========")

    critical_issues = [
        issue for issue in ai_review.issues
        if str(issue.severity).upper().endswith("CRITICAL")
    ]

    passed = (
        not python_issues
        and not critical_issues
    )

    if passed:
        print("PIPELINE TEST: PASSED")

        approved_script = script.model_dump()
        approved_storyboard = scene_plan.model_dump()

        video_id = create_project(
            approved_script,
            approved_storyboard
            )

        print(f"\nProject created: {video_id}")
        print(f"Saved to: output/{video_id}/")
    else:
        print("PIPELINE TEST: FAILED")
        print("No project was created.")

    print("\n==================================\n")


if __name__ == "__main__":
    run_pipeline_test()