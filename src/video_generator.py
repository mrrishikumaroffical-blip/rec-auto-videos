import os
import requests
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import (
    VideoFileClip, AudioFileClip, TextClip,
    CompositeVideoClip, concatenate_videoclips,
    ColorClip, ImageClip
)

W, H         = 1080, 1920
CHANNEL      = "RishiTech"
ACCENT       = (255, 30, 80)
WHITE        = (255, 255, 255)
YELLOW       = (255, 220, 0)
DARK         = (10, 10, 20)

def get_font(size):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except:
            continue
    return ImageFont.load_default()

def fetch_pexels_videos(query, api_key, count=5):
    headers  = {"Authorization": api_key}
    params   = {"query": query, "per_page": count, "orientation": "portrait"}
    response = requests.get("https://api.pexels.com/videos/search", headers=headers, params=params)
    data     = response.json()
    videos   = []
    for v in data.get("videos", []):
        files = v.get("video_files", [])
        # pick HD portrait file
        for f in files:
            if f.get("width", 0) >= 720 and f.get("height", 0) >= 1280:
                videos.append(f["link"])
                break
        if not videos or len(videos) < count:
            if files:
                videos.append(files[0]["link"])
    return videos[:count]

def download_video(url, path):
    r = requests.get(url, timeout=30, stream=True)
    with open(path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    return path

def wrap_text(text, font, max_width):
    words = text.split()
    lines, line = [], ""
    for word in words:
        test = line + word + " "
        try:
            bbox = font.getbbox(test)
            w    = bbox[2] - bbox[0]
        except:
            w = len(test) * 20
        if w <= max_width:
            line = test
        else:
            if line:
                lines.append(line.strip())
            line = word + " "
    if line:
        lines.append(line.strip())
    return lines

def create_text_overlay(caption, frame_type, frame_num, total_frames):
    img  = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # ── Dark gradient overlay ─────────────────────────────────
    for i in range(H):
        alpha = int(180 * (i / H) ** 0.5)
        draw.rectangle([(0, i), (W, i+1)], fill=(0, 0, 0, alpha))

    # ── Top bar ───────────────────────────────────────────────
    draw.rectangle([(0, 0), (W, 100)], fill=(10, 10, 20, 220))
    draw.rectangle([(0, 0), (6, 100)], fill=(*ACCENT, 255))

    font_ch = get_font(42)
    draw.text((25, 28), f"▶  {CHANNEL}", font=font_ch, fill=(*WHITE, 255))

    # Live badge
    draw.rounded_rectangle([(W-150, 20), (W-20, 78)], radius=8, fill=(*ACCENT, 255))
    font_badge = get_font(30)
    draw.text((W-85, 49), "LIVE", font=font_badge, fill=(*WHITE, 255), anchor="mm")

    # ── Breaking tag ──────────────────────────────────────────
    if frame_type == "hook":
        font_tag = get_font(34)
        draw.rounded_rectangle([(30, 120), (370, 168)], radius=6, fill=(*ACCENT, 255))
        draw.text((200, 144), "⚡ BREAKING NEWS", font=font_tag,
                  fill=(*WHITE, 255), anchor="mm")

    # ── Main text ─────────────────────────────────────────────
    font_main = get_font(78) if frame_type == "hook" else get_font(66)
    padding   = 60
    lines     = wrap_text(caption, font_main, W - padding * 2)

    total_h = len(lines) * 95
    y       = H // 2 - total_h // 2 + 100

    for i, line in enumerate(lines):
        # Shadow
        draw.text((W//2 + 3, y + 3), line, font=font_main,
                  fill=(0, 0, 0, 200), anchor="mm")
        # Text color
        if frame_type == "hook" and i == 0:
            color = (*YELLOW, 255)
        else:
            color = (*WHITE, 255)
        draw.text((W//2, y), line, font=font_main, fill=color, anchor="mm")
        y += 95

    # ── Progress bar ──────────────────────────────────────────
    draw.rectangle([(0, H-8), (W, H)], fill=(40, 40, 60, 255))
    prog = int(W * (frame_num + 1) / total_frames)
    draw.rectangle([(0, H-8), (prog, H)], fill=(*ACCENT, 255))

    # ── Bottom CTA ────────────────────────────────────────────
    draw.rectangle([(0, H-100), (W, H-10)], fill=(10, 10, 20, 200))
    font_cta = get_font(34)
    draw.text((W//2, H-55), "👆 FOLLOW FOR DAILY AI & TECH NEWS",
              font=font_cta, fill=(180, 180, 200, 255), anchor="mm")

    return img

def extract_captions(script):
    captions, types = [], []
    for line in script.split("\n"):
        if line.startswith("HOOK:"):
            captions.append(line.replace("HOOK:", "").strip())
            types.append("hook")
        elif line.startswith("BODY:"):
            text  = line.replace("BODY:", "").strip()
            words = text.split()
            size  = 12
            for i in range(0, len(words), size):
                captions.append(" ".join(words[i:i+size]))
                types.append("body")
        elif line.startswith("CTA:"):
            captions.append(line.replace("CTA:", "").strip())
            types.append("cta")
    return captions, types

def create_video(narration_path, script, api_key):
    print("\n🎬 Starting Video Generator...")
    print("─" * 40)

    audio    = AudioFileClip(narration_path)
    duration = audio.duration
    print(f"  ✅ Audio: {duration:.1f}s")

    captions, types = extract_captions(script)
    if not captions:
        captions = ["AI is changing everything", "Are you ready?"]
        types    = ["hook", "body"]

    num_frames    = len(captions)
    clip_duration = duration / num_frames

    # Fetch video clips
    print("  Fetching Pexels videos...")
    queries = ["artificial intelligence technology", "future technology digital",
               "computer data science", "smartphone technology"]
    videos  = []
    for q in queries:
        v = fetch_pexels_videos(q, api_key, count=2)
        videos.extend(v)
        if len(videos) >= num_frames:
            break

    if not videos:
        print("  ⚠️  No videos found, using images")
        videos = None

    os.makedirs("data/videos/clips", exist_ok=True)
    os.makedirs("data/videos/frames", exist_ok=True)

    final_clips = []

    for i, (caption, ftype) in enumerate(zip(captions, types)):
        print(f"  Processing frame {i+1}/{num_frames}...")

        try:
            if videos and i < len(videos):
                # Download video clip
                vid_path = f"data/videos/clips/clip_{i}.mp4"
                download_video(videos[i], vid_path)

                # Load and resize video clip
                clip = VideoFileClip(vid_path)

                # Loop if clip is shorter than needed
                if clip.duration < clip_duration:
                    clip = clip.loop(duration=clip_duration)
                else:
                    clip = clip.subclip(0, clip_duration)

                # Resize to portrait
                clip = clip.resize((W, H))

            else:
                # Fallback: black background
                clip = ColorClip(size=(W, H), color=DARK, duration=clip_duration)

        except Exception as e:
            print(f"  ⚠️  Video error: {e}, using fallback")
            clip = ColorClip(size=(W, H), color=DARK, duration=clip_duration)

        # Create text overlay
        overlay_img  = create_text_overlay(caption, ftype, i, num_frames)
        overlay_path = f"data/videos/frames/overlay_{i}.png"
        overlay_img.save(overlay_path)

        overlay_clip = ImageClip(overlay_path).set_duration(clip_duration)
        composite    = CompositeVideoClip([clip, overlay_clip])
        final_clips.append(composite)

    print("  Combining clips...")
    final = concatenate_videoclips(final_clips, method="compose")
    final = final.set_audio(audio)

    out = "data/videos/final_video.mp4"
    print("  Rendering final video...")
    final.write_videofile(
        out, fps=24, codec="libx264",
        audio_codec="aac", verbose=False, logger=None
    )

    size = os.path.getsize(out) / 1024 / 1024
    print(f"  ✅ Done! {size:.1f} MB")
    print("─" * 40)
    return out
