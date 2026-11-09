import json
import re
from pathlib import Path

BASE_DIR = Path("output/video_001")

STORYBOARD_PATH = BASE_DIR / "storyboard.json"
TIMESTAMPS_PATH = BASE_DIR / "audio/timestamps.json"
OUTPUT_PATH = BASE_DIR / "scene_timings.json"


def normalize(text):
    return re.findall(r"[a-z0-9']+", text.lower())


def main():
    with open(STORYBOARD_PATH) as f:
        storyboard = json.load(f)

    with open(TIMESTAMPS_PATH) as f:
        timestamps = json.load(f)

    timestamp_words = [
        normalize(item["word"])
        for item in timestamps
    ]

    timestamp_words = [
        word[0] if word else ""
        for word in timestamp_words
    ]

    scene_timings = []
    current_position = 0

    for scene in storyboard["scenes"]:
        narration_words = normalize(scene["narration"])
        matched = False

        for start in range(current_position, len(timestamp_words)):
            end = start + len(narration_words)

            if timestamp_words[start:end] == narration_words:
                scene_timings.append({
                    "scene_number": scene["scene_number"],
                    "image": f"images/scene_{scene['scene_number']:02d}.png",
                    "start": timestamps[start]["start"],
                    "end": timestamps[end - 1]["end"],
                    "duration": round(
                        timestamps[end - 1]["end"] -
                        timestamps[start]["start"], 3
                    )
                })

                current_position = end
                matched = True
                break

        if not matched:
            raise ValueError(
                f"Could not match narration for scene "
                f"{scene['scene_number']}: {scene['narration']}"
            )

    with open(OUTPUT_PATH, "w") as f:
        json.dump(scene_timings, f, indent=4)

    print("Scene timings generated successfully!")

    for scene in scene_timings:
        print(
            f"Scene {scene['scene_number']}: "
            f"{scene['start']}s - {scene['end']}s"
        )


if __name__ == "__main__":
    main()