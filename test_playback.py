# play_audio.py

from pydub import AudioSegment
from pydub.playback import play
import os
#local
from load_ffmpeg import load_ffmpeg

ffmpeg_path, ffprobe_path = load_ffmpeg()

# Register paths with pydub
AudioSegment.converter = ffmpeg_path
AudioSegment.ffprobe = ffprobe_path

# Path to audio file
file_path = os.path.join("voice_tests", "tts-1-hd_alloy.mp3")

# Try to play the audio
try:
    print(f"🔊 Loading: {file_path}")
    audio = AudioSegment.from_mp3(file_path)
    print("▶️ Playing audio...")
    play(audio)
    print("✅ Done.")
except Exception as e:
    print(f"❌ Failed to play audio: {e}")
