"""The floating Tkinter window."""
import ctypes
import sys
import threading
import time
import tkinter as tk

import pytesseract
import requests

from . import config
from .capture import grab_screen, read_text
from .llm import ask, image_message

FONT = "Segoe UI"  # falls back to the system font on Linux
BG, FG, MUTED, ACCENT, ACCENT_DARK = "#1e1e1e", "#f5f5f5", "#8a8a8a", "#3b82f6", "#2563eb"


class App:
    def __init__(self):
        if sys.platform == "win32":
            # mss switches Windows to real-pixel coordinates on its first capture. Do it before the window exists,
            # otherwise on a scaled display (e.g. 125%) the window drifts off the right edge after that capture.
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        root = self.root = tk.Tk()
        self.w = root.winfo_pixels("180p")  # width in points, so it scales with the display
        root.title("SnapSolve")
        root.overrideredirect(True)  # no border / title bar
        root.attributes("-topmost", True)
        root.configure(bg=BG, highlightthickness=1, highlightbackground="#333")

        bar = tk.Frame(root, bg=BG)
        bar.pack(fill="x", padx=10, pady=(10, 6))
        self.btn = tk.Button(
            bar, text="⛶  Capture", command=self.on_click, font=(FONT, 10, "bold"),
            bg=ACCENT, fg="white", activebackground=ACCENT_DARK, activeforeground="white",
            disabledforeground="#dbeafe", relief="flat", bd=0, padx=12, pady=5, cursor="hand2",
        )
        self.btn.pack(side="left")
        tk.Button(
            bar, text="✕", command=root.destroy, font=(FONT, 11), bg=BG, fg=MUTED,
            activebackground=BG, activeforeground=FG, relief="flat", bd=0, cursor="hand2",
        ).pack(side="right")

        self.answer = tk.Label(root, text=f"Ready ({config.MODE} mode)", font=(FONT, 13, "bold"), bg=BG, fg=FG,
                               wraplength=self.w - 20, justify="left", anchor="w")
        self.answer.pack(fill="x", padx=10)
        self.time = tk.Label(root, text="Right-click to close", font=(FONT, 9), bg=BG, fg=MUTED, anchor="w")
        self.time.pack(fill="x", padx=10, pady=(2, 10))

        root.bind_all("<Button-3>", lambda e: root.destroy())  # right-click anywhere to exit
        self.dock()

    def dock(self):
        # Pin the window flush to the right edge, vertically centred; re-run whenever the height changes.
        self.root.update_idletasks()
        h = self.root.winfo_reqheight()
        self.root.geometry(f"{self.w}x{h}+{self.root.winfo_screenwidth() - self.w}+{(self.root.winfo_screenheight() - h) // 2}")

    def run(self):
        self.root.mainloop()

    def on_click(self):
        self.btn.config(text="⏳  Thinking...", state="disabled")
        self.root.withdraw()  # hide the popup so it isn't in the screenshot
        # Wait 100ms so the screen redraws without it, then work in a background thread.
        # daemon=True: a hung request won't keep the app alive after you close it.
        self.root.after(100, threading.Thread(target=self.solve, daemon=True).start)

    def solve(self):
        # Runs in a background thread: screen grab, OCR and the API call all happen here.
        start, path = time.perf_counter(), None
        try:
            image, path = grab_screen()
            self.root.after(0, self.root.deiconify)  # show the popup again while OCR and the API run
            if config.MODE == "image":
                result = ask(image_message(image))
            else:
                text = read_text(image)
                result = ask(text) if text else "No text detected."
        except pytesseract.TesseractNotFoundError:
            result = "Tesseract not found. Install it or set TESSERACT_CMD in .env."
        except requests.HTTPError as e:
            result = f"API error {e.response.status_code}: {e.response.reason}"  # e.g. "API error 503: Service Unavailable"
        except requests.RequestException as e:
            result = f"API error: {e}"
        except Exception as e:
            result = f"Error: {e}"
        elapsed = time.perf_counter() - start
        if path:
            path.with_suffix(".txt").write_text(f"{result}\n{elapsed:.2f}s", encoding="utf-8")  # answer + time saved next to the screenshot
        # Tkinter widgets must only be touched from the main thread, so hand the result back via after().
        self.root.after(0, self.show, result, elapsed)

    def show(self, result, elapsed):
        self.root.deiconify()  # in case the capture itself failed
        self.answer.config(text=result)
        self.time.config(text=f"⏱  {elapsed:.2f}s")
        self.btn.config(text="⛶  Capture", state="normal")
        self.dock()
