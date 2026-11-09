"""
Run this file with voice_env/bin/python.

Creates:
- audio/narration.wav
- audio/timestamps.json
- audio/captions.srt
- scene_timings.json
- final_video.mp4
"""

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path
from difflib import SequenceMatcher

from kokoro_mlx import KokoroTTS
from faster_whisper import WhisperModel


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_ROOT = PROJECT_ROOT / "output"

WIDTH = 1080
HEIGHT = 1920
FPS = 30
WORDS_PER_CAPTION = 5
VOICE = "af_heart"
VOICE_SPEED = 1.0
WHISPER_MODEL = "base"

CAPTION_FONT_SIZE = 8
CAPTION_MARGIN_V = 30
CAPTION_OUTLINE = 0.2


def normalize(text: str) -> list[str]:
    words = re.findall(r"[a-z0-9']+", text.lower())

    return [
        word.replace("'", "")
        for word in words
    ]


def get_duration(path: Path, ffprobe: str) -> float:
    result = subprocess.run(
        [
            ffprobe, "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path)
        ],
        capture_output=True,
        text=True,
        check=True
    )
    return float(result.stdout.strip())


def format_timestamp(seconds: float) -> str:
    milliseconds = int(round(seconds * 1000))
    hours = milliseconds // 3_600_000
    milliseconds %= 3_600_000
    minutes = milliseconds // 60_000
    milliseconds %= 60_000
    secs = milliseconds // 1000
    milliseconds %= 1000
    return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"


def generate_voiceover(text: str, audio_path: Path) -> None:
    audio_path.parent.mkdir(parents=True, exist_ok=True)
    with KokoroTTS.from_pretrained() as tts:
        result = tts.save(
            text,
            str(audio_path),
            voice=VOICE,
            speed=VOICE_SPEED,
            sample_rate=24000
        )
    print(f"Voice generated: {result.duration:.2f} seconds")


def generate_word_timestamps(audio_path: Path, output_path: Path) -> list[dict]:
    print("Loading Whisper base model...")
    model = WhisperModel(
        WHISPER_MODEL,
        device="cpu",
        compute_type="int8"
    )
    segments, _ = model.transcribe(
        str(audio_path),
        word_timestamps=True
    )

    words = []
    for segment in segments:
        for word in segment.words or []:
            words.append({
                "word": word.word.strip(),
                "start": round(word.start, 3),
                "end": round(word.end, 3)
            })

    if not words:
        raise RuntimeError("Whisper did not detect any spoken words.")

    output_path.write_text(
        json.dumps(words, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )
    print(f"Detected {len(words)} words.")
    return words


def find_scene_images(project_dir: Path, storyboard: dict) -> list[Path]:
    image_dir = project_dir / "images"
    image_paths = []

    for scene in storyboard["scenes"]:
        number = scene["scene_number"]
        matches = [
            path for path in image_dir.glob(f"scene_{number:02d}.*")
            if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
        ]
        if not matches:
            raise FileNotFoundError(
                f"Missing image for Scene {number}. Upload every scene image first."
            )
        if len(matches) > 1:
            raise RuntimeError(
                f"Multiple image files found for Scene {number}. "
                "Keep only one image per scene."
            )
        image_paths.append(matches[0])

    return image_paths


def generate_scene_timings(
    storyboard: dict,
    words: list[dict],
    image_paths: list[Path],
    project_dir: Path,
    output_path: Path
) -> list[dict]:
    # Flatten Whisper words into tokens, remembering which word each came from.
    whisper_tokens, token_to_word = [], []
    for i, item in enumerate(words):
        for tok in normalize(item["word"]):
            whisper_tokens.append(tok)
            token_to_word.append(i)

    # Flatten narration into tokens, remembering which scene each belongs to.
    narr_tokens, token_to_scene = [], []
    for s_idx, scene in enumerate(storyboard["scenes"]):
        for tok in normalize(scene["narration"]):
            narr_tokens.append(tok)
            token_to_scene.append(s_idx)

    # Fuzzy-align, so one misheard word doesn't break the render.
    matcher = SequenceMatcher(None, narr_tokens, whisper_tokens, autojunk=False)
    first_word, last_word = {}, {}
    for a, b, size in matcher.get_matching_blocks():
        for k in range(size):
            s = token_to_scene[a + k]
            w = token_to_word[b + k]
            first_word.setdefault(s, w)
            last_word[s] = w

    scene_timings = []
    for s_idx, (scene, image_path) in enumerate(
        zip(storyboard["scenes"], image_paths)
    ):
        if s_idx not in first_word:
            raise ValueError(
                f"Could not align Whisper timestamps with Scene "
                f"{scene['scene_number']}: {scene['narration']}"
            )
        start = words[first_word[s_idx]]["start"]
        end = words[last_word[s_idx]]["end"]
        scene_timings.append({
            "scene_number": scene["scene_number"],
            "image": str(image_path.relative_to(project_dir)),
            "start": start,
            "end": end,
            "duration": round(end - start, 3),
        })

    output_path.write_text(
        json.dumps(scene_timings, indent=4),
        encoding="utf-8"
    )
    return scene_timings


def project_dir_for(image_path: Path, timings_path: Path) -> Path:
    # Images are stored at <project>/images and timings at <project>/scene_timings.json.
    return timings_path.parent


def generate_captions(words: list[dict], output_path: Path) -> None:
    lines = []
    for index in range(0, len(words), WORDS_PER_CAPTION):
        chunk = words[index:index + WORDS_PER_CAPTION]
        lines.extend([
            str(index // WORDS_PER_CAPTION + 1),
            f"{format_timestamp(chunk[0]['start'])} --> "
            f"{format_timestamp(chunk[-1]['end'])}",
            " ".join(item["word"] for item in chunk),
            ""
        ])
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Generated {len(words[::WORDS_PER_CAPTION])} subtitle groups.")


def render_video(
    project_dir: Path,
    scene_timings: list[dict],
    audio_path: Path,
    captions_path: Path,
    output_path: Path
) -> None:
    ffmpeg = "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"
    ffprobe = "/opt/homebrew/opt/ffmpeg-full/bin/ffprobe"

    if not Path(ffmpeg).exists():
        raise FileNotFoundError("FFmpeg not found. Install or configure FFmpeg.")
    if not Path(ffprobe).exists():
        raise FileNotFoundError("FFprobe not found. Install or configure FFprobe.")

    audio_duration = get_duration(audio_path, ffprobe)
    starts = [scene["start"] for scene in scene_timings]
    starts[0] = 0.0

    durations = []
    for index in range(len(scene_timings)):
        end = starts[index + 1] if index + 1 < len(starts) else audio_duration
        durations.append(end - starts[index])

    if any(duration <= 0 for duration in durations):
        raise ValueError("A scene has zero or negative duration.")

    concat_path = project_dir / "image_sequence.txt"
    with concat_path.open("w", encoding="utf-8") as file:
        for scene, duration in zip(scene_timings, durations):
            image_path = (project_dir / scene["image"]).resolve()
            if not image_path.exists():
                raise FileNotFoundError(image_path)
            safe_path = str(image_path).replace("'", r"'\''")
            file.write(f"file '{safe_path}'\n")
            file.write(f"duration {duration:.3f}\n")

        last_image = (project_dir / scene_timings[-1]["image"]).resolve()
        safe_last = str(last_image).replace("'", r"'\''")
        file.write(f"file '{safe_last}'\n")

    escaped_subtitle_path = str(captions_path.resolve()).replace(":", r"\:")
    video_filter = (
        f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,"
        f"crop={WIDTH}:{HEIGHT},setsar=1,fps={FPS},"
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
        ffmpeg, "-y",
        "-f", "concat", "-safe", "0", "-i", str(concat_path),
        "-i", str(audio_path),
        "-map", "0:v:0", "-map", "1:a:0",
        "-vf", video_filter,
        "-r", str(FPS),
        "-c:v", "libx264", "-preset", "ultrafast",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-ar", "24000", "-ac", "1",
        "-t", str(audio_duration),
        "-movflags", "+faststart",
        str(output_path)
    ]

    print("Rendering final video...")
    subprocess.run(command, check=True)
    print(f"Video rendered: {output_path}")


def run(project_id: str) -> Path:
    project_dir = OUTPUT_ROOT / project_id
    script_path = project_dir / "script.json"
    storyboard_path = project_dir / "storyboard.json"

    if not script_path.exists() or not storyboard_path.exists():
        raise FileNotFoundError("Project script or storyboard is missing.")

    script = json.loads(script_path.read_text(encoding="utf-8"))
    storyboard = json.loads(storyboard_path.read_text(encoding="utf-8"))

    image_paths = find_scene_images(project_dir, storyboard)
    audio_dir = project_dir / "audio"
    audio_path = audio_dir / "narration.wav"
    timestamps_path = audio_dir / "timestamps.json"
    captions_path = audio_dir / "captions.srt"
    timings_path = project_dir / "scene_timings.json"
    output_path = project_dir / "final_video.mp4"

    generate_voiceover(script["full_script"], audio_path)
    words = generate_word_timestamps(audio_path, timestamps_path)
    scene_timings = generate_scene_timings(
        storyboard,
        words,
        image_paths,
        project_dir,
        timings_path
    )
    generate_captions(words, captions_path)
    render_video(
        project_dir,
        scene_timings,
        audio_path,
        captions_path,
        output_path
    )
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-id", required=True)
    args = parser.parse_args()
    result = run(args.project_id)
    print(f"FINAL_VIDEO={result}")
