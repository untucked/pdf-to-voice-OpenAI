# main_OpenAI.py
import os
import textwrap
from pydub import AudioSegment
import configparser
import sys
import tkinter as tk
from tkinter import filedialog
config = configparser.ConfigParser()
config.read('config.conf')
from pydub.utils import which

# local
import support
from load_ffmpeg import load_ffmpeg

ffmpeg_path, ffprobe_path = load_ffmpeg()

AudioSegment.converter = ffmpeg_path
AudioSegment.ffprobe = ffprobe_path


test_load_pdf = False
# === CONFIG ===
if test_load_pdf:
    pdf_path = config.get('read', 'read_essay', fallback='Tell-Tale_Heart.pdf')
else:
    # Prompt user to choose a file via GUI
    root = tk.Tk()
    root.withdraw()  # Hide the empty Tkinter window
    pdf_path = filedialog.askopenfilename(
        title="Select a PDF to read",
        filetypes=[("PDF files", "*.pdf")],
    )

    if not pdf_path:
        raise ValueError("No file selected — exiting.")

    print(f"📄 Selected file: {pdf_path}")
if not os.path.exists(pdf_path):
    raise FileNotFoundError(f"❌ PDF not found at: {pdf_path}")
output_dir = config.get('read', 'output_dir', fallback='output')
chunk_size = 3300  # Safe limit for tts-1 (under ~4,096 characters)

os.makedirs(output_dir, exist_ok=True)

# === EXTRACT TEXT FROM PDF ===
full_text = support.get_full_text(pdf_path)

# === SPLIT INTO CHUNKS ===
chunks = textwrap.wrap(full_text, chunk_size, break_long_words=False, break_on_hyphens=False)

# === CONVERT EACH CHUNK TO MP3 ===
# Get the base name (filename with extension, but no directory)
base_name = os.path.basename(pdf_path)
# Split the base name into name and extension
file_name_without_extension, _ = os.path.splitext(base_name)
# Now use the cleaned name for your MP3 file
mp3_name = f'{file_name_without_extension}_mp3'
support.convert_to_mp3_openai(chunks, output_dir, name=mp3_name,
                   test_script=False)

# === MERGE ALL MP3 FILES ===
support.merge_mp3s(AudioSegment, mp3_name, output_dir=output_dir,clean_mp3s=False)

