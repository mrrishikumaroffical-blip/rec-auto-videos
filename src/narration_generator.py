import os
from gtts import gTTS

def extract_script_text(script):
    text = ""
    for line in script.split("\n"):
        for tag in ["HOOK:", "BODY:", "CTA:"]:
            if line.startswith(tag):
                text += line.replace(tag, "").strip() + " "
    return text.strip()

def generate_narration(script):
    print("\n🎙️  Starting Narration Generator...")
    print("─" * 40)

    text = extract_script_text(script)
    print(f"  ✅ Script text extracted")
    print(f"  📝 Text: {text[:100]}...")

    os.makedirs("data/videos", exist_ok=True)
    output_path = "data/videos/narration.mp3"

    print("  Generating voiceover...")
    tts = gTTS(text=text, lang="en", slow=False)
    tts.save(output_path)

    size = os.path.getsize(output_path)
    print(f"  ✅ Narration saved: {output_path}")
    print(f"  ✅ File size: {size} bytes")
    print("─" * 40)
    print("✅ Done!")
    print("─" * 40)

    return output_path
