import requests

url = "http://localhost:11434/api/generate"

payload = {
    "model": "qwen3:4b",
    "prompt": """
    Write a 100-word YouTube Shorts narration about
    why people replay conversations after they happen.

    Explain post-event processing accurately.
    Start with a compelling hook.
    Include a relatable example.
    End with a thought-provoking observation.

    Use natural conversational English.
    Avoid repetition and clichés.
    Return only the narration.
    """,
    "stream": False
}

response = requests.post(url, json=payload)

if response.status_code == 200:
    result = response.json()
    print("\nGENERATED SCRIPT:\n")
    print(result["response"])
else:
    print("Error:", response.text)