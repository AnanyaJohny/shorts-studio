import json
from pathlib import Path


OUTPUT_DIR = Path("output")


def create_project(
    script_data: dict,
    storyboard_data: dict
) -> str:
    """
    Create a new video project and save its approved
    script and storyboard.
    Returns the unique video ID.
    """

    OUTPUT_DIR.mkdir(exist_ok=True)

    # Find existing video project folders
    existing_projects = [
        path for path in OUTPUT_DIR.iterdir()
        if path.is_dir() and path.name.startswith("video_")
    ]

    # Generate the next video ID
    existing_numbers = []

    for project in existing_projects:
        try:
            number = int(project.name.replace("video_", ""))
            existing_numbers.append(number)
        except ValueError:
            continue

    next_number = max(existing_numbers, default=0) + 1
    video_id = f"video_{next_number:03d}"

    # Create project folder
    project_dir = OUTPUT_DIR / video_id
    project_dir.mkdir()

    # Save approved script
    with open(
        project_dir / "script.json",
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            script_data,
            file,
            indent=4,
            ensure_ascii=False
        )

    # Save approved storyboard
    with open(
        project_dir / "storyboard.json",
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            storyboard_data,
            file,
            indent=4,
            ensure_ascii=False
        )

    return video_id