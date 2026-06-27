import os
import json
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

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

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    result = response.choices[0].message.content
    return result

def parse_final_score(result):
    for line in result.split("\n"):
        if "Final Score:" in line:
            try:
                raw = line.split(":")[1].strip().replace("/100","").replace("/10","").strip()
                score = float(raw) if float(raw) <= 10 else float(raw)/10
                return score
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
        print("   Pipeline stopped.")
        return None, 0
