import json
import re
import os
from datetime import datetime

def clean_text(text):
    text = re.sub(r"<.*?>", "", text)
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^a-zA-Z0-9\s.,!?]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def extract_keywords(title, summary):
    IMPORTANT_WORDS = [
        "ai", "artificial intelligence", "machine learning", "data science",
        "programming", "startup", "software", "cybersecurity", "robotics",
        "space", "google", "microsoft", "openai", "meta", "apple", "nvidia",
        "python", "llm", "gpt", "automation", "cloud", "semiconductor",
        "chatgpt", "gemini", "claude", "robot", "launch", "new", "release"
    ]
    text = (title + " " + summary).lower()
    found = [word for word in IMPORTANT_WORDS if word in text]
    return found

def rank_articles(articles):
    for article in articles:
        keywords = extract_keywords(article["title"], article["summary"])
        article["keywords"]      = keywords
        article["keyword_score"] = len(keywords)
        article["title"]         = clean_text(article["title"])
        article["summary"]       = clean_text(article["summary"])
    ranked = sorted(articles, key=lambda x: x["keyword_score"], reverse=True)
    return ranked[:10]

def clean_and_rank():
    print("\n🧹 Starting Data Cleaner...")
    print("─" * 40)

    import glob
    files = glob.glob("data/raw_news/*.json")
    if not files:
        print("❌ No news file found!")
        return []

    with open(files[-1]) as f:
        articles = json.load(f)
    print(f"  ✅ Loaded: {len(articles)} articles")

    ranked = rank_articles(articles)
    print(f"  ✅ Top {len(ranked)} articles ranked")

    os.makedirs("data/cleaned_news", exist_ok=True)
    today    = datetime.now().strftime("%Y-%m-%d")
    filepath = f"data/cleaned_news/ranked_{today}.json"

    with open(filepath, "w") as f:
        json.dump(ranked, f, indent=2)
    print(f"  ✅ Saved: {filepath}")

    print("─" * 40)
    print("✅ Done!")
    print("─" * 40)
    return ranked
