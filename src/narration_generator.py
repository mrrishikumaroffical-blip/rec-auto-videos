import os
import re
import asyncio
import edge_tts

def extract_script_text(script):
    lines = script.split("\n")
    text  = ""
    for line in lines:
        for tag in ["HOOK:", "BODY:", "CTA:"]:
            if line.startswith(tag):
                text += line.replace(tag, "").strip() + " "
    return text.strip()

async def generate_audio(text, output_path):
    communicate = edge_tts.Communicate(
        text=text,
        voice="en-US-ChristopherNeural",
        rate="+10%"
    )
    await communicate.save(output_path)

def generate_narration(script):
    print("\n🎙️  Starting Narration Generator...")
    print("─" * 40)

    text = extract_script_text(script)
    print(f"  ✅ Script text extracted")
    print(f"  📝 Text: {text[:100]}...")

    os.makedirs("data/videos", exist_ok=True)
    output_path = "data/videos/narration.mp3"

    print("  Generating voiceover...")
    asyncio.run(generate_audio(text, output_path))

    size = os.path.getsize(output_path)
    print(f"  ✅ Narration saved: {output_path}")
    print(f"  ✅ File size: {size} bytes")
    print("─" * 40)
    print("✅ Done!")
    print("─" * 40)

    return output_path
