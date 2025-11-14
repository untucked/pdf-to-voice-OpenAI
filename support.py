# support.py
import re
import pdfplumber
import os
import time
from datetime import timedelta
import pytesseract
from pdf2image import convert_from_path
import openai
import configparser
import sys
from pathlib import Path
from pydub import AudioSegment
from pydub.playback import play

def clean_text(text):
    # Remove bracketed [1], parenthetical (12)
    text = re.sub(r'\[\d+\]', '', text)
    # text = re.sub(r'\(\d+\)', '', text)
    # Remove sequences like "word 1 ." or "2 ," etc.
    text = re.sub(r'\b\d{1,3}\s+[.,](?=\s)', '.', text)
    text = re.sub(r'(?<=[a-z])\s\d{1,2}\.(?=\s|$)', ',', text)
    # Remove sequences like "25% 15 )."
    text = re.sub(r'(?<=\S)\s\d{1,3}\s*\)\.', '.', text)
    # Remove ref numbers after a valid year followed by `)` and more refs: "2024) 17 23"
    text = re.sub(r'((?:19|20)\d{2})\)\s+((?:\d{1,3}\s+)+)', r'\1 ', text)
    # Remove patterns like "2023 9 –" → "2023 –"
    text = re.sub(r'\b\d{1,3}(?=\s*[–-])', '', text)
    # Remove inline sequences like " 1 2 ." or "4\n5 ."
    text = re.sub(r'(?<=\s)(\d{1,3}(\s+|\n)+)+(?=[\.,\n])', '.', text)
    # Collapse multiple spaces
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()

def remove_references_section(text: str) -> str:
    # Match "References" (case-insensitive), followed by anything until the end of the text
    # also look for "Sources" and "Bibliography"
    text = re.sub(r'\b(references|sources|bibliography)\b.*', '', text, flags=re.IGNORECASE | re.DOTALL)
    return text

def init_pytesseract():
    config = configparser.ConfigParser()
    config.read('config.conf')

    tesseract_path = config.get('paths', 'tesseract_path', fallback=None)
    if not tesseract_path or not tesseract_path.strip():
        print('❌ Error: tesseract_path is not configured in the CONF file.', file=sys.stderr)
        raise ValueError('Need to configure tesseract_path in order to run this script.')

    pytesseract.pytesseract.tesseract_cmd = tesseract_path

    poppler_bin = config.get('paths', 'poppler_bin', fallback=None)
    if not poppler_bin or not poppler_bin.strip():
        print('❌ Error: poppler_bin is not configured in the CONF file.', file=sys.stderr)
        raise ValueError('Need to configure poppler_bin in order to run this script.')

    return poppler_bin

def get_full_text_ocr(pdf_path):
    poppler_bin = init_pytesseract()
    full_text = ""

    try:
        pages = convert_from_path(pdf_path, poppler_path=poppler_bin, dpi=300)
    except Exception as e:
        raise RuntimeError(f"🚨 Failed to convert PDF to images: {e}")
    # remove references section if it exists

    for i, page_image in enumerate(pages):
        print(f"Running OCR on page {i + 1}")
        text = pytesseract.image_to_string(page_image)
        if i==0:
            print(text)
        cleaned = clean_text(text)
        full_text += f"\n\n[Page {i + 1}]\n{cleaned}"
    return full_text

def get_full_text(pdf_path, print_text=False):    
    full_text = ""
    image_based_file=False
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Total pages: {len(pdf.pages)}")
        # determine if pdf is image based - if the first 2-5 pages are blank we know it's a picture based pdf and needs to be converted to text
        # Check only the first 3 pages for real text
        scanned_blank_pages = 0
        for page_num in range(min(3, len(pdf.pages))):
            page = pdf.pages[page_num]
            text = page.extract_text()
            if print_text:
                print(f"[Scan Check] Page {page_num + 1} text: {repr(text)}")
            if not text or not text.strip():
                scanned_blank_pages += 1

        if scanned_blank_pages == min(3, len(pdf.pages)):
            print("First 3 pages are blank – likely image-based PDF. Switching to OCR...")
            image_based_file = True
        else:
            print("Text found in first 3 pages moving forward with reading pdf")

        # OCR fallback if image-based
        if image_based_file:
            return get_full_text_ocr(pdf_path)
        
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if print_text:
                print(f"Page {page_num + 1} text: {repr(text)}")
            if text:
                print(f"Adding page {page_num + 1}")
                # print(text)
                cleaned_text = clean_text(text)
                # print(cleaned_text)
                full_text += f"\n{cleaned_text}"
        full_text = remove_references_section(full_text)
    return full_text

def convert_to_mp3_openai(chunks, output_dir, name="output", test_script=False, voice="echo", model="tts-1",
                          include_part_intro=False):
    timestamps_path = os.path.join(output_dir, f"{name}_timestamps.txt")
    pad_width = len(str(len(chunks)))
    with open(timestamps_path, "w") as ts_file:
        total_time = 0
        for i, chunk in enumerate(chunks):
            print(f"🎤 Generating chunk {i+1}/{len(chunks)}...")
            output_mp3 = os.path.join(output_dir, f"{name}_part{str(i+1).zfill(pad_width)}.mp3")
            if os.path.exists(output_mp3):
                print(f"📁 {output_mp3} exists — skipping.")
                continue

            # Generate speech with OpenAI
            if include_part_intro:
                include_intro = f"Part {i+1}. "
            else:
                include_intro = ""
            try:
                response = openai.audio.speech.create(
                    model=model,
                    voice=voice,
                    input=f"{include_intro} {chunk}",
                    response_format="mp3",
                )
                with open(output_mp3, "wb") as f:
                    f.write(response.content)

                # Calculate duration using pydub
                audio = AudioSegment.from_mp3(output_mp3)
                duration = audio.duration_seconds
                ts_file.write(f"Part {i+1}: {str(timedelta(seconds=int(total_time)))}\n")
                total_time += duration

                if test_script:
                    abs_path = str(Path(output_mp3).resolve())
                    try:
                        audio = AudioSegment.from_mp3(abs_path)
                        audio_length_seconds = audio.duration_seconds
                        print(f"📏 Audio length: {audio_length_seconds:.2f} seconds")
                        print(f"▶️ Playing: {abs_path}")
                        play(audio)
                        print(f"🎧 Finished playing: {voice}")
                        time.sleep(audio_length_seconds + 0.5)  # slight delay to avoid overlap
                    except Exception as e:
                        print(f"❌ Failed to play audio for '{voice}': {e}")

            except Exception as e:
                print(f"❌ Failed to generate chunk {i+1}: {e}")

def extract_part_number(filename):
    match = re.search(r'_part(\d+)\.mp3$', filename)
    return int(match.group(1)) if match else float('inf')

def merge_mp3s(AudioSegment, mp3_name, output_dir='output',
               clean_mp3s=False):
    print("🔊 Merging all MP3s into one file...")

    merged_audio = AudioSegment.empty()
    pause = AudioSegment.silent(duration=250)  # 0.25 seconds of silence

    # Ensure correct order by sorting
    mp3_files = sorted([
        f for f in os.listdir(output_dir)
        if f.startswith(mp3_name) and f.endswith(".mp3") and not f.endswith("_full.mp3")
    ], key=extract_part_number)
    timestamps = []
    current_duration_ms = 0  # in milliseconds
    for i, filename in enumerate(mp3_files, 1):
        part_path = os.path.join(output_dir, filename)
        if not os.path.exists(part_path):
            print(f"⚠️ File not found: {part_path}. Skipping.")
            continue

        # === Load the main part audio
        print(f"🔍 Trying to load: {part_path}")
        if not os.path.exists(part_path):
            raise FileNotFoundError(f"❌ File not found: {part_path}")
        part_audio = AudioSegment.from_mp3(part_path)

        # === Record timestamp BEFORE adding this section
        timestamp_str = str(timedelta(milliseconds=current_duration_ms))
        timestamps.append(f"Part {i} - {timestamp_str}")

        # === Concatenate: [Part Intro] + [Pause] + [Part Audio] + [Pause]
        merged_audio += part_audio + pause
        current_duration_ms += len(part_audio) + len(pause)

    # === Export final merged audio
    final_output = os.path.join(output_dir, f"{mp3_name}_full.mp3")
    merged_audio.export(final_output, format="mp3")
    
    if clean_mp3s:
        # Optional: clear old MP3 files
        for f in os.listdir(output_dir):
            if f.endswith('.mp3') and f!=f"{mp3_name}_full.mp3":
                os.remove(os.path.join(output_dir, f))

    # Save timestamps to file
    timestamp_file = os.path.join(output_dir, "timestamps.txt")
    with open(timestamp_file, 'w') as f:
        for line in timestamps:
            f.write(line + '\n')

    print(f"🕒 Timestamps saved to:\n{timestamp_file}")
    print(f"✅ Merged audio with intros saved to:\n{final_output}")

if __name__ == "__main__":
    from pydub import AudioSegment
    config = configparser.ConfigParser()
    config.read('config.conf')
    from pydub.utils import which
    output_dir = config.get('read', 'output_dir', fallback='output')

    # Set paths BEFORE importing AudioSegment
    ffmpeg_path = config.get('paths', 'ffmpeg_path', fallback=None)
    if not ffmpeg_path or not ffmpeg_path.strip():
        raise ValueError("❌ 'ffmpeg_path' is missing from config.conf")
    elif not os.path.isfile(ffmpeg_path):
        raise FileNotFoundError(f"❌ ffmpeg_path is set to '{ffmpeg_path}', but that file does not exist.")


    ffprobe_path = config.get('paths', 'ffmpeg_probe', fallback=None)
    if not ffprobe_path or not ffprobe_path.strip():
        raise ValueError("❌ 'ffmpeg_probe' is missing from config.conf")
    elif not os.path.isfile(ffprobe_path):
        raise FileNotFoundError(f"❌ ffmpeg_probe is set to '{ffprobe_path}', but that file does not exist.")


    AudioSegment.converter = ffmpeg_path

    os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_path)  # Add to PATH at runtime

    AudioSegment.converter = ffmpeg_path
    AudioSegment.ffprobe = ffprobe_path

    pdf_path = r'C:\Users\eylan\Downloads\Oscar Health (OSCR) Deep Dive.pdf'
    print(f"📄 Selected file: {pdf_path}")
    base_name = os.path.basename(pdf_path)
    file_name_without_extension, _ = os.path.splitext(base_name)
    mp3_name = f'{file_name_without_extension}_mp3'
    merge_mp3s(AudioSegment, mp3_name, output_dir=output_dir,clean_mp3s=False)