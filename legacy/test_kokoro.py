from kokoro_mlx import KokoroTTS

text = """
Have you ever replayed an awkward conversation in your head?
You remember exactly what happened, but your mind keeps searching
for things you could have said differently.
Maybe you wonder whether your joke sounded strange,
or whether the other person misunderstood you.
Psychologists often call this kind of repetitive thinking
post-event processing, particularly in the context of social anxiety.
Instead of helping you solve anything new,
your mind keeps returning to the same moment.
The next time this happens, try noticing the thought
without treating every imagined mistake as a fact.
A conversation is one moment,
not a complete judgment of who you are.
"""

with KokoroTTS.from_pretrained() as tts:

    result = tts.save(
        text,
        "output/video_001/audio/narration.wav",
        voice="af_heart",
        speed=1.0,
        sample_rate=24000
    )

    print("Voice generation complete!")
    print(f"Duration: {result.duration:.2f} seconds")
    print(f"Voice: {result.voice}")