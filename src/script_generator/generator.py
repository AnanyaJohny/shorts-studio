from src.llm import generate_json
from src.script_generator.models import ScriptDraft


def generate_script(topic: str) -> ScriptDraft:
    prompt = f"""
    You are a professional YouTube Shorts scriptwriter
    specialising in psychology and human behaviour.
    Create a YouTube Short about: {topic}
    REQUIREMENTS:
    - Write 100-110 words for the full narration.
    - Start with an intriguing, relatable hook.
    - Explain exactly ONE psychological concept.
    - Explain the concept accurately without exaggeration.
    - Include a relatable everyday example.
    - Include one genuinely interesting insight.
    - End with a memorable takeaway.
    - Use natural, conversational English.
    - Avoid generic motivational statements.
    - Avoid calling every psychological behaviour a survival mechanism.
    - Do not invent scientific studies, statistics, or research findings.
    - Do not present speculation as established science.
    - Avoid repeating the same idea in different sentences.
    Return the following information:
    - title
    - topic
    - hook
    - full_script
    - takeaway
    """

    generated_data = generate_json(
        prompt=prompt,
        response_schema=ScriptDraft.model_json_schema(),
        options={
            "temperature": 0.5,
            "num_predict": 700,
            "num_ctx": 4096,
        },
    )

    script = ScriptDraft.model_validate_json(generated_data)
    return script