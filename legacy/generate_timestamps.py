import json
from faster_whisper import WhisperModel

AUDIO_PATH = "output/video_005/audio/narration.wav"
OUTPUT_PATH = "output/video_005/audio/timestamps.json"

print("Loading Whisper model...")

model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)

print("Transcribing narration...")

segments, info = model.transcribe(
    AUDIO_PATH,
    word_timestamps=True
)

words = []

for segment in segments:
    for word in segment.words:
        words.append({
            "word": word.word.strip(),
            "start": round(word.start, 3),
            "end": round(word.end, 3)
        })

with open(OUTPUT_PATH, "w") as file:
    json.dump(words, file, indent=4)

print("Transcription complete!")
print(f"Detected {len(words)} words.")
print(f"Saved timestamps to {OUTPUT_PATH}")