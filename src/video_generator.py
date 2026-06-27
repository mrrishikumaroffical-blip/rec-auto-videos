import os
import requests
import json
from moviepy.editor import (
    AudioFileClip, ImageClip, concatenate_videoclips,
    TextClip, CompositeVideoClip
)
from PIL import Image
import numpy as np

def fetch_pexels_images(query, api_key, count=5):
    headers = {"Authorization": api_key}
    params  = {"query": query, "per_page": count, "orientation": "portrait"}
    response = requests.get("https://api.pexels.com/v1/search", headers=headers, params=params)
    data     = response.json()
    urls     = [p["src"]["large"] for p in data.get("photos", [])]
    return urls

def download_image(url, path):
    response = requests.get(url, timeout=10)
    with open(path, "wb") as f:
        f.write(response.content)
    img = Image.open(path).resize((1080, 1920))
    img.save(path)
    return path

def create_video(narration_path, script, api_key):
    print("\n🎬 Starting Video Generator...")
    print("─" * 40)

    audio     = AudioFileClip(narration_path)
    duration  = audio.duration
    print(f"  ✅ Audio duration: {duration:.1f} seconds")

    print("  Fetching images from Pexels...")
    query  = "artificial intelligence technology"
    images = fetch_pexels_images(query, api_key, count=5)
    print(f"  ✅ Found {len(images)} images")

    os.makedirs("data/videos/frames", exist_ok=True)
    clips        = []
    clip_duration = duration / len(images)

    for i, url in enumerate(images):
        path = f"data/videos/frames/frame_{i}.jpg"
        download_image(url, path)
        clip = ImageClip(path).set_duration(clip_duration)
        clips.append(clip)
        print(f"  ✅ Frame {i+1} ready")

    video = concatenate_videoclips(clips, method="compose")
    video = video.set_audio(audio)

    output_path = "data/videos/final_video.mp4"
    print("  Rendering video...")
    video.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        verbose=False,
        logger=None
    )

    size = os.path.getsize(output_path)
    print(f"  ✅ Video saved: {output_path}")
    print(f"  ✅ File size: {size/1024/1024:.1f} MB")
    print("─" * 40)
    print("✅ Done!")
    print("─" * 40)

    return output_path
