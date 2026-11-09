from src.script_generator.generator import generate_script


def main():

    topic = "Why do we overthink conversations after they happen?"

    print("Generating your YouTube Short...")

    script = generate_script(topic)

    print("\nTITLE:", script.title)

    print("\nHOOK:", script.hook)

    print("\nFULL SCRIPT:", script.full_script)

    print("\nSCENES:")

    for scene in script.scenes:
        print(f"\nScene {scene.scene_number}")
        print("Narration:", scene.narration)
        print("Visual:", scene.visual_description)
        print("Duration:", scene.duration_seconds)


if __name__ == "__main__":
    main()