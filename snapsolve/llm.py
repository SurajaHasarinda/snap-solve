"""Sends the OCR text or the screenshot to an OpenAI-compatible chat API."""
import base64
import io
import time
from urllib.parse import urlsplit

import requests

from . import config

http = requests.Session()  # reuses the connection, so calls after the first are quicker

extra = {"reasoning_effort": "none"}


def keep_warm():
    # Runs in a daemon thread: a cheap HEAD request to the API host (no tokens, no quota) keeps the
    # TLS connection in the session pool open.
    u = urlsplit(config.API_URL)
    while u.scheme:
        try:
            http.head(f"{u.scheme}://{u.netloc}", timeout=5)
        except requests.RequestException:
            pass
        time.sleep(config.KEEP_WARM)


def image_message(image):
    # The screenshot as a JPEG data URL in the OpenAI vision format; JPEG uploads much faster than PNG.
    buf = io.BytesIO()
    image.save(buf, "JPEG", quality=85)
    return [
        {"type": "text", "text": "."},  # vision APIs require a text part alongside the image; the system prompt has the real instructions
        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()}},
    ]


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
