import configparser
import os

def load_ffmpeg():
    # Load config
    config = configparser.ConfigParser()
    config.read('config.conf')

    # Get ffmpeg and ffprobe paths
    ffmpeg_path = config.get('paths', 'ffmpeg_path')
    ffprobe_path = config.get('paths', 'ffmpeg_probe')

    # Validate paths
    if not os.path.isfile(ffmpeg_path):
        raise FileNotFoundError(f"❌ ffmpeg not found at: {ffmpeg_path}")
    if not os.path.isfile(ffprobe_path):
        raise FileNotFoundError(f"❌ ffprobe not found at: {ffprobe_path}")

    return ffmpeg_path, ffprobe_path