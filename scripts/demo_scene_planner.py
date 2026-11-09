from src.scene_planner.planner import generate_scene_plan


script = """
Ever feel like you're rewatching a conversation in your head?
Your brain keeps revisiting what happened.
For example, after an argument with a friend,
you might wonder what you should have said differently.
Sometimes, these thoughts keep repeating long after the conversation ends.
"""


print("Generating scene plan...\n")

scene_plan = generate_scene_plan(script)

for scene in scene_plan.scenes:
    print(f"\nSCENE {scene.scene_number}")
    print("Narration:", scene.narration)
    print("Visual:", scene.visual_description)

print("\nTotal scenes:", len(scene_plan.scenes))