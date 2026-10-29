# AI Property Video Generator

A small Streamlit prototype for the assignment brief. It accepts property details and photos, creates a scene plan and factual template-based voice-over script, and exports a captioned MP4. It uses only details entered by the user; no AI API key is required.

## Features
- Property name, location, price, type, features and CTA form
- JPG/JPEG/PNG photo uploads (4–8 recommended)
- Caption overlays, gentle zoom effect and fade transitions
- MP4 export with in-app preview/download
- Generated scene list and suggested narration script
- Helpful validation for missing details/images

## Requirements
- Python 3.10 or newer
- VS Code
- Internet connection for installing Python packages

## Run in VS Code (Windows)
1. Extract the ZIP file.
2. Open VS Code and select **File → Open Folder**. Choose `AI_Property_Video_Generator`.
3. Open **Terminal → New Terminal**.
4. Create a virtual environment:
   ```powershell
   py -m venv .venv
   ```
5. Activate it:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
   If PowerShell blocks activation, run this once in that terminal:
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\.venv\Scripts\Activate.ps1
   ```
   Or use Command Prompt terminal and run:
   ```bat
   .venv\Scripts\activate.bat
   ```
6. Install dependencies:
   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
7. Start the app:
   ```powershell
   streamlit run app.py
   ```
8. The app opens in your browser (usually `http://localhost:8501`). Enter property details, upload 4–8 photos, and click **Generate property video**. Use the download button to save the MP4.

## Sample data
Open `sample_data/sample_property.json` for the example listing and use the included sample images to test the app.

## Implementation notes and limitations
- Video frames are created with OpenCV and exported as MP4.
- Captions and narration copy use deterministic template logic, not a hosted LLM.
- This prototype does not synthesize spoken narration or add background music.
- OpenCV codec support can vary by operating system. If MP4 writing fails, install a current Python/OpenCV build and try again.
- Use synthetic data only. Review all text before publishing.

## Demo checklist
1. Launch the app.
2. Fill in or keep the sample property details.
3. Upload the sample images.
4. Generate and preview the MP4.
5. Download the MP4 and show the scene captions and voice-over script.
