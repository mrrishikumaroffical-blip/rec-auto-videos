import os
import json
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
        "temperature": 0.7
    }
    response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
    return response.json()["choices"][0]["message"]["content"]

def score_topic(article):
    prompt = f"""
You are a viral content expert for YouTube Shorts.

Analyze this tech news article and give scores out of 10:

Title: {article["title"]}
Summary: {article["summary"]}

Give scores in this EXACT format:
Topic Popularity: X/10
Hook Strength: X/10
Viewer Curiosity: X/10
Competition: X/10
Search Trend: X/10
Retention Potential: X/10
Final Score: X/10
Verdict: PASS or REJECT
Reason: one sentence why
"""
    return call_groq(prompt)

def parse_final_score(result):
    for line in result.split("\n"):
        if "Final Score:" in line:
            try:
                raw = line.split(":")[1].strip().replace("/10","").replace("/100","").strip()
                score = float(raw)
                return score if score <= 10 else score/10
            except:
                return 0.0
    return 0.0

def run_viral_scorer(ranked_articles):
    print("\n🔥 Starting Viral Scorer...")
    print("─" * 40)

    best_article = None
    best_score   = 0
    best_result  = None

    for i, article in enumerate(ranked_articles[:5]):
        print(f"\n  Scoring article {i+1}: {article['title'][:50]}...")
        result = score_topic(article)
        score  = parse_final_score(result)
        print(f"  Final Score: {score}/10")

        if score >= 7 and score > best_score:
            best_score   = score
            best_article = article
            best_result  = result

    print("\n" + "─" * 40)

    if best_article:
        print(f"✅ PASS! Best topic selected:")
        print(f"   {best_article['title']}")
        print(f"   Score: {best_score}/10")
        print("\nFull Analysis:")
        print(best_result)
        return best_article, best_score
    else:
        print("❌ REJECTED! No topic scored >= 7")
        return None, 0
