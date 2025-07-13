
# PDF to Voice (OpenAI Edition)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-TTS-green)

## 🎧 Introduction
This tool converts PDF files into spoken audio (MP3). It handles:
- **Text-based PDFs** using `pdfplumber`
- **Image-based PDFs** (like scanned documents) using **OCR** with `Tesseract` + `Poppler`
- **Speech synthesis** using OpenAI's `tts-1` or `tts-1-hd` models

Why? Because I don’t want to pay for Adobe’s read-aloud tools — and now I don’t need to.

---

## 🎯 Goal
- Convert any PDF (text or scanned image) to MP3 audio
- Automatically detect if OCR is needed and fall back to it
- Create chunked audio files and merge them with optional part intros
- Save timestamps for easy reference
- Choose from various OpenAI voice models
- Use with GUI-based PDF picker or set path in config

---

## ⚙️ How It Works
1. **PDF Detection**: Checks the first 3 pages to determine if OCR is needed.
2. **Extraction**:
   - Uses `pdfplumber` for regular text PDFs.
   - Falls back to `pytesseract` + `pdf2image` for scanned PDFs.
3. **Audio Conversion**:
   - Breaks text into chunks (~3300 characters for OpenAI).
   - Uses OpenAI’s `tts-1` or `tts-1-hd` to generate MP3s.
4. **Merging**:
   - Combines MP3s with optional pauses.
   - Outputs a final MP3 and `timestamps.txt`.

---

## ✨ Features
- ✅ Auto OCR fallback for scanned/image-based PDFs
- 🧠 Intelligent text cleaning and reference removal
- 🎙️ OpenAI voice generation with part intros
- 🔊 MP3 merging with optional silence between sections
- 📝 Timestamp file for audio reference
- 🧪 Test OpenAI voices individually using `test_voices.py` or `test_playback.py`

---

## 📁 Files
- `main_OpenAI.py`: Main script with GUI or config path input
- `support.py`: All logic for cleaning, OCR, conversion, merging
- `load_ffmpeg.py`: Utility to load ffmpeg/ffprobe correctly
- `test_voices.py`: Generate and play samples of all OpenAI voices
- `test_playback.py`: Play any MP3 file using `pydub` with ffmpeg backend

---

## 🧪 Testing OpenAI Voices
Use `test_voices.py`:
```bash
python test_voices.py
```
You can modify `voices = [...]` to test different voices. Default is `tts-1-hd` model with all 9 supported voices.

Use `test_playback.py` to play an existing MP3:
```bash
python test_playback.py voice_tests/tts-1-hd_echo.mp3
```

---

## 📦 Dependencies
- Python 3.10+
- openai
- pydub
- pdfplumber
- pytesseract
- pdf2image
- tkinter
- ffmpeg + ffprobe
- tesseract OCR
- poppler (for `pdf2image`)

---

## 🛠 ffmpeg / ffprobe Setup (Windows)
1. Download from [Gyan.dev](https://www.gyan.dev/ffmpeg/builds/)
2. Unzip to a safe location
3. Add `bin/` to your PATH
4. Confirm:
```bash
ffmpeg -version
ffprobe -version
```

---

## 🧠 Tesseract & Poppler Setup
- [Tesseract Windows Installer](https://github.com/UB-Mannheim/tesseract/wiki)
- [Poppler Windows Release](https://github.com/oschwartz10612/poppler-windows/releases/)

---

## 📁 Cloning & Pushing to Git
```bash
git clone https://github.com/untucked/pdf-to-voice-OpenAI.git
cd pdf-to-voice
```

Push code:
```bash
git init
git add .
git commit -m "Initialize"
git branch -M main
git remote add origin https://github.com/untucked/pdf-to-voice-OpenAI.git
git push -u origin main
```

---

## 🐳 Optional: Containerization
To ensure it runs on any system, consider containerizing this with Docker. Example `Dockerfile` can be provided on request.

---

## 📝 License
MIT © Bradley Eylander
