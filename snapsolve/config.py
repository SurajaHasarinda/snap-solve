"""Settings from .env, file paths, and the default system prompt."""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

API_URL = os.getenv("API_URL", "")
API_KEY = os.getenv("API_KEY", "")
MODEL = os.getenv("MODEL", "")
TESSERACT_CMD = os.getenv("TESSERACT_CMD")

SHOTS_DIR = ROOT / "screenshots"
PROMPT_FILE = ROOT / "prompt.txt"
DEFAULT_PROMPT = """You are an ultra-fast quiz solver. You will receive raw, potentially messy OCR text of a multiple-choice question.
Strict rules:
1. Deduce the question and options, ignoring typos.
2. Output ONLY the correct option letter and exact text of the correct answer.
3. ZERO explanation.
4. DO NOT use introductory phrases.
Example Output: B) Paris"""

SHOTS_DIR.mkdir(exist_ok=True)
if not PROMPT_FILE.exists():
    PROMPT_FILE.write_text(DEFAULT_PROMPT, encoding="utf-8")


def system_prompt():
    # Read on every call so edits to prompt.txt apply without a restart.
    return PROMPT_FILE.read_text(encoding="utf-8")
