"""Sends the OCR text to an OpenAI-compatible chat API."""
import requests

from . import config

http = requests.Session()  # reuses the connection, so calls after the first are quicker

extra = {"reasoning_effort": "none"}


def ask(question):
    global extra
    r = http.post(
        config.API_URL,
        headers={"Authorization": f"Bearer {config.API_KEY}"},
        json={
            "model": config.MODEL,
            "messages": [
                {"role": "system", "content": config.system_prompt()},
                {"role": "user", "content": question},
            ],
            "max_tokens": 15,
            "temperature": 0.1,
            **extra,
        },
        timeout=15,
    )
    if r.status_code == 400 and extra:
        extra = {}
        return ask(question)
    r.raise_for_status()
    content = r.json()["choices"][0]["message"].get("content")
    return content.strip() if content else "(empty response, try again)"
