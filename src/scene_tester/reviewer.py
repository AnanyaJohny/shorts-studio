import json

from src.llm import generate_json
from src.scene_tester.models import SceneReview


def review_scenes(script: str, scene_plan: dict) -> SceneReview:

    scenes_json = json.dumps(
        scene_plan,
        ensure_ascii=False,
        indent=2
    )

    prompt = f"""
You are a visual quality reviewer for YouTube Shorts.

Your task is to evaluate the visual descriptions in a storyboard.

ORIGINAL SCRIPT:
{script}

GENERATED SCENES:
{scenes_json}

EVALUATE ONLY THESE CRITERIA:

1. VISUAL RELEVANCE:
Does each visual description communicate the meaning
of its corresponding narration?

2. VISUAL CLARITY:
Can viewers understand the visual without reading text?

3. SIMPLICITY:
Does each scene communicate one clear visual idea?

4. STYLE CONSISTENCY:
Are the illustrations consistent with this style?
- Minimalist black stickman illustrations.
- Clean white background.
- Simple objects and expressions.
- No written text inside illustrations.

IMPORTANT RULES:

- Review only the scenes actually provided.
- Never invent additional scenes or scene numbers.
- Never claim that a scene is duplicated unless you
  can identify the exact duplicate in the provided data.
- Do not evaluate script coverage or narration repetition.
  Python validation handles those checks.
- Do not demand literal illustrations of abstract concepts.
- Accept reasonable visual metaphors.
- Do not reject a scene simply because another metaphor
  could be more creative.
- Do not invent problems.
- Only genuinely confusing, misleading, irrelevant or
  style-inconsistent visuals should be reported.

ISSUE SEVERITY:

CRITICAL:
The visual directly contradicts the narration,
communicates a completely different concept,
or is irrelevant to the narration.

MINOR:
The visual could be clearer, simpler or more intuitive.

Only CRITICAL issues should cause passed to be false.
Minor issues must not cause rejection.

For every issue, identify the actual scene number.

If there are no critical issues, set passed to true.
Keep each issue, explanation and suggested_fix under 20 words.
Return only valid JSON matching the required schema.
"""

    generated_data = generate_json(
        prompt=prompt,
        response_schema=SceneReview.model_json_schema(),
        options={
            "temperature": 0.2,
            "num_predict": 3000,
            "num_ctx": 8192
        }

        
    )

    review = SceneReview.model_validate_json(generated_data)

    return review