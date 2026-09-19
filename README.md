# SnapSolve 📸🤫

Floating always-on-top window that screenshots your screen, reads the multiple-choice question with Tesseract, and shows the answer from an LLM.

## Setup & Run

| | Windows (PowerShell) | Ubuntu |
|---|---|---|
| Setup | `.\setup.ps1` | `bash setup.sh` |
| Run | `.\run.ps1` | `bash run.sh` |

Then put your API details in `.env`. Set `MODE=image` to send the screenshot straight to the model instead of reading it with OCR first (needs a model that accepts images).

Ubuntu: log in with an **Xorg** session (choose it on the login screen). Screen capture doesn't work on Wayland.

Click **Capture** to solve. Right-click the window to close.

- Edit `prompt.txt` to change the system prompt (created with the default on first run; changes apply immediately).
- Screenshots are saved in `screenshots/`.
