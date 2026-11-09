from src.scene_tester.controller import create_approved_scene_plan


script = """
Have you ever replayed an awkward conversation in your head?
You remember exactly what happened, but your mind keeps
searching for things you could have said differently.

Maybe you wonder whether your joke sounded strange,
or whether the other person misunderstood you.

Psychologists often call this kind of repetitive thinking
post-event processing, particularly in the context of
social anxiety.

Instead of helping you solve anything new,
your mind keeps returning to the same moment.

The next time this happens, try noticing the thought
without treating every imagined mistake as a fact.
A conversation is one moment, not a complete judgment
of who you are.
"""

print("Starting automated storyboard generation...")

approved_plan = create_approved_scene_plan(script)

if approved_plan:
    print("\nFinal approved storyboard:")
    for scene in approved_plan.scenes:
        print(f"\nScene {scene.scene_number}")
        print("Narration:", scene.narration)
        print("Visual:", scene.visual_description)
        print("Duration:", scene.duration_seconds)
else:
    print("\nStoryboard requires human review.")