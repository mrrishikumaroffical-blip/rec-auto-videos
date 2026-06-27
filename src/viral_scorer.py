import os
import json
import httpx
from groq import Groq

# Fix httpx proxies issue
if not hasattr(httpx, "_orig_client"):
    _orig_init = httpx.Client.__init__
    def _patched_init(self, *args, **kwargs):
        kwargs.pop("proxies", None)
        _orig_init(self, *args, **kwargs)
    httpx.Client.__init__ = _patched_init

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
    return response.choices[0].message.content

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
