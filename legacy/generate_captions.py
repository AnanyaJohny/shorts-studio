import json
from pathlib import Path

BASE_DIR = Path("output/video_001")

TIMESTAMPS_PATH = BASE_DIR / "audio/timestamps.json"
OUTPUT_PATH = BASE_DIR / "audio/captions.srt"

WORDS_PER_CAPTION = 5


def format_timestamp(seconds):
    milliseconds = int(seconds * 1000)

    hours = milliseconds // 3600000
    milliseconds %= 3600000

    minutes = milliseconds // 60000
    milliseconds %= 60000

    seconds = milliseconds // 1000
    milliseconds %= 1000

    return (
        f"{hours:02}:{minutes:02}:"
        f"{seconds:02},{milliseconds:03}"
    )


def main():
    with open(TIMESTAMPS_PATH) as f:
        words = json.load(f)

    captions = []

    for i in range(0, len(words), WORDS_PER_CAPTION):
        chunk = words[i:i + WORDS_PER_CAPTION]

        start = chunk[0]["start"]
        end = chunk[-1]["end"]

        text = " ".join(word["word"] for word in chunk)

        captions.append({
            "start": start,
            "end": end,
            "text": text
        })

    with open(OUTPUT_PATH, "w") as f:
        for index, caption in enumerate(captions, start=1):
            f.write(f"{index}\n")
            f.write(
                f"{format_timestamp(caption['start'])} --> "
                f"{format_timestamp(caption['end'])}\n"
            )
            f.write(f"{caption['text']}\n\n")

    print(f"Generated {len(captions)} captions!")
    print(f"Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()