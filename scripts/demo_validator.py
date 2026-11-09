from src.scene_planner.models import Scene, ScenePlan
from src.scene_tester.tester import test_scene_plan


original_script = """
Ever feel like you're rewatching a conversation in your head?
Your brain keeps revisiting what happened.
For example, after an argument with a friend,
you might wonder what you should have said differently.
Sometimes, these thoughts keep repeating long after the conversation ends.
"""


# Simulate the flawed scene plan from our previous test.
# Five scenes are intentionally used to test scene-count validation.
scene_plan = ScenePlan(
    scenes=[
        Scene(
            scene_number=1,
            narration="Ever feel like you're rewatching a conversation in your head?",
            visual_description="Stickman watching a conversation."
        ),
        Scene(
            scene_number=2,
            narration="Your brain keeps revisiting what happened.",
            visual_description="Stickman with a thought bubble."
        ),
        Scene(
            scene_number=3,
            narration="For example, after an argument with a friend",
            visual_description="Two stickmen arguing."
        ),
        Scene(
            scene_number=4,
            narration="you might wonder what you should have said differently.",
            visual_description="Stickman thinking."
        ),
        Scene(
            scene_number=5,
            narration="Sometimes, these thoughts keep repeating long after the conversation ends.",
            visual_description="Stickman with a repeating thought bubble."
        )
    ]
)


result = test_scene_plan(
    original_script,
    scene_plan
)