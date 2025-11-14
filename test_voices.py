# test_voices.py
import openai
import os
from pydub.utils import which
import sys
import time
from pathlib import Path
#local
from load_ffmpeg import load_ffmpeg

ffmpeg_path, ffprobe_path = load_ffmpeg()

# Now import AudioSegment
from pydub import AudioSegment
from pydub.playback import play

AudioSegment.converter = ffmpeg_path
AudioSegment.ffprobe = ffprobe_path


# Set your OpenAI API key here or via environment variable
openai.api_key = os.getenv("OPENAI_API_KEY") or "your-api-key-here"

voices = [
    "alloy", "ash", "coral", "echo",
    "fable", "nova", 
    "onyx", "sage", 
    "shimmer"
]

sample_text = "This is a test of the OpenAI text-to-speech voice:"


# Choose between 'tts-1' and 'tts-1-hd'
model = "tts-1-hd"

output_dir = "voice_tests"
os.makedirs(output_dir, exist_ok=True)

print(voices)
for voice in voices:
    file_path = os.path.join(output_dir, f"{model}_{voice}.mp3")
    if os.path.exists(file_path):
        print(f"📁 File already exists: {file_path} — skipping generation.")
    else:
        print(f"🔊 Generating voice sample: {voice}")
        response = openai.audio.speech.create(
            model=model,
            voice=voice,
            input=f"{sample_text} {voice}",
            response_format="mp3",
        )

        file_path = os.path.join(output_dir, f"{model}_{voice}.mp3")
        with open(file_path, "wb") as f:
            f.write(response.content)       

        print(f"✅ Saved: {file_path}")

    print(f"▶️ Playing: {voice}")
    try:
        audio = AudioSegment.from_mp3(file_path)
        audio_length_seconds = audio.duration_seconds
        print(f"📏 Audio length: {audio_length_seconds:.2f} seconds") # Print the length
        play(audio)
        print(f"🎧 Finished playing: {voice}")
        time.sleep(audio_length_seconds + 0.5) # slight delay to avoid overlap
    except Exception as e:
        print(f"❌ Failed to play '{voice}': {e}")
        continue  # Continue loop even if playback fails


print("\nAll voice tests completed.")