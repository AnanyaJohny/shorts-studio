import json
import subprocess
from pathlib import Path

BASE_DIR = Path("output/video_001")
TIMINGS_PATH = BASE_DIR / "scene_timings.json"
AUDIO_PATH = BASE_DIR / "audio/narration.wav"
CAPTIONS_PATH = BASE_DIR / "audio/captions.srt"
OUTPUT_PATH = BASE_DIR / "final_video.mp4"

FFMPEG = "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"
FFPROBE = "/opt/homebrew/opt/ffmpeg-full/bin/ffprobe"

WIDTH = 1080
HEIGHT = 1920
FPS = 30

# Caption style. IMPORTANT: for .srt files, FFmpeg/libass pretends the screen is
# only 384 x 288 units, then scales everything up to 1080 x 1920 (about 6.7x).
# So these numbers are NOT pixels:
#   FontSize 10  -> about 67 px tall text on the final video
#   MarginV  45  -> about 300 px above the bottom edge
#   Outline   1  -> about 7 px outline
CAPTION_FONT_SIZE = 10
CAPTION_MARGIN_V = 45
CAPTION_OUTLINE = 0.2


def get_duration(path):
    """Ask ffprobe how long a media file is, in seconds."""
    result = subprocess.run(
        [FFPROBE, "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(result.stdout.strip())


def main():
    for path in [TIMINGS_PATH, AUDIO_PATH, CAPTIONS_PATH]:
        if not path.exists():
            raise FileNotFoundError(path)

    with open(TIMINGS_PATH) as f:
        scenes = json.load(f)

    audio_duration = get_duration(AUDIO_PATH)

    # Each image stays on screen until the NEXT scene starts.
    # The first image starts at 0, the last image lasts until the audio ends.
    # This keeps images in sync with the narration and makes the video exactly
    # as long as the audio, even if the timings file has small gaps.
    starts = [scene["start"] for scene in scenes]
    starts[0] = 0.0
    durations = []
    for i in range(len(scenes)):
        end = starts[i + 1] if i + 1 < len(scenes) else audio_duration
        durations.append(end - starts[i])

    print(f"Audio length: {audio_duration:.2f}s")
    for scene, duration in zip(scenes, durations):
        print(f"  {scene['image']}: {duration:.2f}s")
    print(f"Total of image durations: {sum(durations):.2f}s")
    if any(d <= 0 for d in durations):
        raise ValueError("A scene has zero or negative duration. Check scene_timings.json")

    concat_file = BASE_DIR / "image_sequence.txt"
    with open(concat_file, "w") as f:
        for scene, duration in zip(scenes, durations):
            image_path = (BASE_DIR / scene["image"]).resolve()
            if not image_path.exists():
                raise FileNotFoundError(image_path)
            f.write(f"file '{image_path}'\n")
            f.write(f"duration {duration:.3f}\n")
        # The concat format ignores the duration of the very last entry,
        # so the last image must be listed one extra time.
        last_image = (BASE_DIR / scenes[-1]["image"]).resolve()
        f.write(f"file '{last_image}'\n")

    subtitle_path = str(CAPTIONS_PATH.resolve())
    escaped_subtitle_path = subtitle_path.replace(":", r"\:")
    video_filter = (
        f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,"
        f"crop={WIDTH}:{HEIGHT},"
        "setsar=1,"
        f"fps={FPS},"
        f"subtitles=filename={escaped_subtitle_path}:"
        "force_style='FontName=Arial"
        f"\\,FontSize={CAPTION_FONT_SIZE}"
        "\\,PrimaryColour=&H000000&"
        "\\,BackColour=&H00FFFFFF"
        "\\,BorderStyle=1"
        f"\\,Outline={CAPTION_OUTLINE}"
        "\\,Shadow=0"
        "\\,Alignment=2"
        f"\\,MarginV={CAPTION_MARGIN_V}'"
    )

    
    command = [
    FFMPEG,
    "-y",

    # Video input
    "-f", "concat",
    "-safe", "0",
    "-i", str(concat_file),

    # Narration input
    "-i", str(AUDIO_PATH),

    # Explicit stream mapping
    "-map", "0:v:0",
    "-map", "1:a:0",

    # Video processing
    "-vf", video_filter,
    "-r", str(FPS),
    "-c:v", "libx264",
    "-preset", "ultrafast",
    "-pix_fmt", "yuv420p",

    # Audio processing
    "-c:a", "aac",
    "-b:a", "192k",
    "-ar", "24000",
    "-ac", "1",

    # Duration
    "-t", str(audio_duration),

    "-movflags", "+faststart",
    str(OUTPUT_PATH),
]

    print("\nRendering your YouTube Short...")
    subprocess.run(command, check=True)
    print("\nVIDEO RENDERED. Now check it (see the verification steps).")
    print(f"Saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()