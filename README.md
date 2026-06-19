# BUZZ AI — 100% Local & Private

A full production-ready RAG (Retrieval-Augmented Generation) AI web application with visual intelligence capabilities, built with a Flask backend and a modern HTML/CSS/JS frontend.

This application runs **100% offline and locally**. It does not use any external APIs, ensuring maximum privacy and zero recurring costs.

## Setup Instructions (One Time)

1. **Install Python dependencies:**
   Make sure you have Python installed. Then run:
   ```bash
   pip install -r requirements.txt
   ```

2. **Download AI model (700MB, free):**
   - Download the free TinyLlama model from:
     [https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf](https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf)
   - Place the downloaded `.gguf` file in the `models/` folder inside this project.

3. **Install Tesseract OCR (for image reading):**
   - Windows: [Download and install from UB-Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
   - Mac: `brew install tesseract`
   - Linux: `sudo apt install tesseract-ocr`

4. **Configure Environment:**
   Create a `.env` file in the root directory (or use the one provided) and fill in the Tesseract path if it's not in your system PATH:
   ```env
   MODEL_PATH=models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
   TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
   ```

5. **Install System Dependencies (For PDF/Office parsing):**
   You also need poppler for PDF image extraction:
   - Windows: Download [poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases) and add the `bin/` folder to your PATH.
   - Linux: `sudo apt install poppler-utils`
   - Mac: `brew install poppler`

## Running the Application

1. Start the Flask server:
   ```bash
   python app.py
   ```
2. Open your web browser and go to:
   ```
   http://localhost:5000
   ```

## Supported Files
PDF, Word (docx), Excel (xlsx), PowerPoint (pptx), Images (jpg/png/webp), CSV, JSON, TXT

## Privacy Guarantee
- **No API keys needed**
- **No internet connection required**
- All files processed on your computer
- Nothing is sent to any server
