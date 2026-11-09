import os
import requests
from dotenv import load_dotenv

load_dotenv()


# Provider configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")

# Ollama configuration
OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434/api/generate"
)

MODEL_NAME = os.getenv("LLM_MODEL", "qwen3:4b")


def generate_json(
    prompt: str,
    response_schema: dict,
    options: dict | None = None
) -> str:
    """
    Generate a structured JSON response using the configured LLM.
    """

    if LLM_PROVIDER == "ollama":
        return _generate_with_ollama(
            prompt,
            response_schema,
            options
        )

    else:
        raise ValueError(
            f"Unsupported LLM provider: {LLM_PROVIDER}"
        )


def _generate_with_ollama(
    prompt: str,
    response_schema: dict,
    options: dict | None = None
) -> str:

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "format": response_schema,
        "stream": False,
        "think": False,
        "options": options or {
            "temperature": 0.5,
            "num_predict": 500,
            "num_ctx": 2048
        }
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=600
    )

    response.raise_for_status()

    result = response.json()

    generated_data = result.get("response", "")

    if not generated_data:
        raise ValueError("Ollama returned an empty response.")

    return generated_data