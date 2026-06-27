import os
import requests

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

def call_groq(prompt):
    headers = {
        "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.8
    }
    response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
    return response.json()["choices"][0]["message"]["content"]

def generate_script(article):
    prompt = f"""
You are a YouTube Shorts script writer.

Write a 45-second viral script for this tech news:
Title: {article["title"]}
Summary: {article["summary"]}

Rules:
- Start with a shocking hook (1 sentence)
- Explain the news simply (3-4 sentences)
- End with a strong CTA (1 sentence)
- Total: 130-150 words
- Conversational tone
- No hashtags, no emojis

Format EXACTLY like this:
HOOK: ...
BODY: ...
CTA: ...
WORD_COUNT: ...
"""
    return call_groq(prompt)

def review_script(script):
    prompt = f"""
You are a YouTube Shorts expert reviewer.

Review this script and improve it:
{script}

Rules:
- Keep it under 150 words
- Make hook more attention grabbing
- Keep simple language
- Return ONLY the improved script in same format:
HOOK: ...
BODY: ...
CTA: ...
WORD_COUNT: ...
"""
    return call_groq(prompt)

def generate_final_script(article):
    print("\n✍️  Starting Script Generator...")
    print("─" * 40)

    print("  Generating first draft...")
    draft = generate_script(article)
    print("  ✅ Draft done")

    print("  Reviewing and improving...")
    final = review_script(draft)
    print("  ✅ Final script ready")

    print("\nFinal Script:")
    print("─" * 40)
    print(final)
    print("─" * 40)

    return final
