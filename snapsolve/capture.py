"""Screen grab (mss) and text extraction (Tesseract)."""
import time

import mss
import mss.tools
import pytesseract
from PIL import Image

from . import config

if config.TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_CMD


def grab_screen():
    # mss copies pixels straight from the screen with no image encoding, which is why it's fast.
    # monitors[0] is every screen stitched together; monitors[1] is the primary monitor.
    # A new MSS() per call because its handle can't be shared across threads.
    with mss.MSS() as sct:
        shot = sct.grab(sct.monitors[1])
    path = config.SHOTS_DIR / f"{time.strftime('%Y%m%d_%H%M%S')}.png"
    mss.tools.to_png(shot.rgb, shot.size, output=str(path))
    return Image.frombytes("RGB", shot.size, shot.rgb), path


def read_text(image):
    # Grayscale + psm 6 (treat the screen as one block of text) skips Tesseract's slow layout analysis.
    return pytesseract.image_to_string(image.convert("L"), config="--psm 6").strip()
