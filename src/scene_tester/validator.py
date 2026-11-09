import re

from src.scene_planner.models import ScenePlan, SceneGrouping


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def validate_scenes(
    original_script: str,
    scene_plan: ScenePlan
) -> list[str]:

    issues = []

    scenes = scene_plan.scenes

    # 1. Check scene count
    if not 6 <= len(scenes) <= 8:
        issues.append(
            f"Expected 6-8 scenes, found {len(scenes)}."
        )

    # 2. Check scene numbering
    scene_numbers = [scene.scene_number for scene in scenes]

    if len(scene_numbers) != len(set(scene_numbers)):
        issues.append("Duplicate scene numbers detected.")

    expected_numbers = list(range(1, len(scenes) + 1))

    if scene_numbers != expected_numbers:
        issues.append("Scene numbers are not sequential.")

    # 3. Check narration and visual descriptions
    for scene in scenes:

        if not scene.narration.strip():
            issues.append(
                f"Scene {scene.scene_number} has empty narration."
            )

        if not scene.visual_description.strip():
            issues.append(
                f"Scene {scene.scene_number} has an empty visual description."
            )

    # 4. Check original narration preservation
    original = normalize_text(original_script)

    combined_narration = normalize_text(
        " ".join(scene.narration for scene in scenes)
    )

    if original != combined_narration:
        issues.append(
            "Scene narration does not exactly preserve "
            "the original script or is in the wrong order."
        )

    # 5. Check duplicate narration
    normalized_scenes = [
        normalize_text(scene.narration)
        for scene in scenes
        if scene.narration.strip()
    ]

    if len(normalized_scenes) != len(set(normalized_scenes)):
        issues.append("Duplicate narration detected.")

    return issues


def validate_grouping(
    grouping: SceneGrouping,
    n_sentences: int
) -> list[str]:

    issues = []
    scenes = grouping.scenes

    # Check scene count.
    if not 6 <= len(scenes) <= 8:
        issues.append(
            f"Expected 6-8 scenes, found {len(scenes)}."
        )

    all_numbers = []

    for scene_index, scene in enumerate(scenes, start=1):

        numbers = scene.sentences

        # Check visual description.
        if not scene.visual_description.strip():
            issues.append(
                f"Scene {scene_index} has an empty visual description."
            )

        # Check for empty sentence groups.
        if not numbers:
            issues.append(
                f"Scene {scene_index} has no sentence numbers."
            )
            continue

        # Check sentence numbers are within range.
        for number in numbers:
            if not 1 <= number <= n_sentences:
                issues.append(
                    f"Scene {scene_index} contains invalid "
                    f"sentence number {number}."
                )

        # Check order within each group.
        if numbers != sorted(numbers):
            issues.append(
                f"Sentence numbers in scene {scene_index} "
                "are not in ascending order."
            )

        # Check that sentences within a group are consecutive.
        if numbers != list(
            range(numbers[0], numbers[-1] + 1)
        ):
            issues.append(
                f"Scene {scene_index} contains non-contiguous "
                "sentence numbers."
            )

        all_numbers.extend(numbers)

    # Check for duplicates.
    if len(all_numbers) != len(set(all_numbers)):
        issues.append("Duplicate sentence numbers detected.")

    # Check for missing sentences.
    expected = list(range(1, n_sentences + 1))

    if sorted(set(all_numbers)) != expected:
        issues.append("One or more sentences are missing.")

    # Check order across scenes.
    if all_numbers != sorted(all_numbers):
        issues.append(
            "Sentence groups are not in the correct order."
        )

    return issues