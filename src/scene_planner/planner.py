from src.llm import generate_json

from src.scene_planner.models import (
    Scene,
    ScenePlan,
    SceneGrouping,
    SceneVisualPlan
)

from src.scene_planner.splitter import (
    split_sentences,
    auto_group
)


def build_scene_plan(sentences, grouping) -> ScenePlan:
    """
    Build scenes using the original sentences.
    Python reconstructs narration exactly.
    """

    scenes = []

    for index, group in enumerate(grouping.scenes, start=1):

        narration_parts = [
            sentences[number - 1]
            for number in group.sentences
        ]

        narration = " ".join(narration_parts)

        scenes.append(
            Scene(
                scene_number=index,
                narration=narration,
                visual_description=group.visual_description
            )
        )

    return ScenePlan(scenes=scenes)


def generate_scene_plan(
    script: str,
    feedback: str = ""
) -> ScenePlan:

    # STEP 1: Split the original narration.
    sentences = split_sentences(script)

    if len(sentences) < 6:
        from src.scene_planner.splitter import split_into_clauses
        sentences = split_into_clauses(
            sentences,
            min_units=6
        )

    if len(sentences) < 6:
        raise ValueError(
            "Could not create at least 6 sentence units."
        )

    # STEP 2: Python groups sentences into scenes.
    fixed_groups = auto_group(sentences, target=7)

    # STEP 3: Prepare narration groups for Qwen.
    grouped_narration = []

    for index, group in enumerate(fixed_groups, start=1):

        narration = " ".join(
            sentences[number - 1]
            for number in group
        )

        grouped_narration.append(
            f"Scene {index}:\n{narration}"
        )

    narration_text = "\n\n".join(grouped_narration)

    # STEP 4: Ask Qwen for visual descriptions only.
    prompt = f"""
You are a professional visual storyboard artist.

Create one visual description for each of the following scenes.

SCENES:
{narration_text}

REQUIREMENTS:
- Return exactly {len(fixed_groups)} scenes.
- Use the same scene numbers, from 1 to {len(fixed_groups)}.
- Each scene must have one clear visual idea.
- Use minimalist black stickman illustrations.
- Use a pure white background.
- Describe character actions, expressions and objects.
- Keep illustrations simple and easy to understand.
- Absolutely NO text, letters, numbers, words, labels,
  captions, emojis or typography inside illustrations.
- Communicate ideas through actions and visual metaphors.

PREVIOUS REVIEW FEEDBACK:
{feedback}

Do not rewrite the narration.
Do not create additional scenes.
Return one visual description for every scene.
"""

    generated_data = generate_json(
        prompt=prompt,
        response_schema=SceneVisualPlan.model_json_schema(),
        options={
            "temperature": 0.4,
            "num_predict": 1000,
            "num_ctx": 4096
        }
    )

    visual_plan = SceneVisualPlan.model_validate_json(
        generated_data
    )

    # STEP 5: Validate Qwen's visual descriptions.
    if len(visual_plan.scenes) != len(fixed_groups):
        raise ValueError(
            "Qwen returned an incorrect number of visual descriptions."
        )

    descriptions = {}

    for visual in visual_plan.scenes:

        if visual.scene_number in descriptions:
            raise ValueError(
                f"Duplicate visual description for scene "
                f"{visual.scene_number}."
            )

        if not 1 <= visual.scene_number <= len(fixed_groups):
            raise ValueError(
                f"Invalid scene number: {visual.scene_number}"
            )

        if not visual.visual_description.strip():
            raise ValueError(
                f"Scene {visual.scene_number} has an empty "
                "visual description."
            )

        descriptions[visual.scene_number] = (
            visual.visual_description
        )

    if len(descriptions) != len(fixed_groups):
        raise ValueError(
            "One or more scene visual descriptions are missing."
        )

    # STEP 6: Reconstruct the final scene plan.
    grouping = SceneGrouping(
        scenes=[
            {
                "sentences": group,
                "visual_description": descriptions[index]
            }
            for index, group in enumerate(fixed_groups, start=1)
        ]
    )

    return build_scene_plan(sentences, grouping)