Set-Location $PSScriptRoot
winget install -e --id UB-Mannheim.TesseractOCR --accept-source-agreements --accept-package-agreements
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
if (-not (Test-Path .env)) { (Get-Content .env.example) -replace '^# TESSERACT_CMD', 'TESSERACT_CMD' | Set-Content .env }
