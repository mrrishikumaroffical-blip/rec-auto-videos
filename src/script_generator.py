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
        "temperature": 0.9
    }
    response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
    return response.json()["choices"][0]["message"]["content"]

def generate_script(article):
    prompt = f"""
You are a viral YouTube Shorts script writer targeting 16-40 year olds in the USA.

Write a script for this tech news:
Title: {article["title"]}
Summary: {article["summary"]}

STRICT RULES:
- Talk directly to viewer using YOU and YOUR
- Start with ONE shocking question that triggers FEAR or CURIOSITY
- Use SHORT simple sentences (max 10 words each)
- Conversational tone like talking to a friend
- Trigger emotions: FEAR, CURIOSITY, PRIDE
- Total: 120-140 words
- NO hashtags, NO emojis, NO complex words

EXACT FORMAT:
HOOK: (1 shocking question - max 15 words)
BODY: (3-4 short punchy sentences using YOU - max 80 words)
CTA: (1 sentence making viewer feel special/smart - max 20 words)
WORD_COUNT: (number)
"""
    return call_groq(prompt)

def review_script(script):
    prompt = f"""
You are a YouTube Shorts expert for US audience aged 16-40.

Review and improve this script:
{script}

STRICT RULES:
- Hook MUST be a shocking question
- Every sentence must use YOU or YOUR
- Each sentence max 10 words
- Must trigger FEAR or CURIOSITY in first 3 seconds
- End with PRIDE emotion
- Keep under 140 words
- Return ONLY improved script in EXACT same format:

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
