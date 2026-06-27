import feedparser
import requests
import json
import hashlib
import os
from datetime import datetime, timezone

RSS_FEEDS = {
    "TechCrunch":  "https://techcrunch.com/feed/",
    "TheVerge":    "https://www.theverge.com/rss/index.xml",
    "Wired":       "https://www.wired.com/feed/rss",
    "ArsTechnica": "https://feeds.arstechnica.com/arstechnica/index",
    "VentureBeat": "https://venturebeat.com/feed/",
}

TECH_KEYWORDS = [
    "ai", "artificial intelligence", "machine learning", "data science",
    "programming", "startup", "software", "cybersecurity", "robotics",
    "space", "google", "microsoft", "openai", "meta", "apple", "nvidia",
    "python", "llm", "gpt", "automation", "cloud", "semiconductor"
]

def make_id(title):
    return hashlib.md5(title.lower().strip().encode()).hexdigest()

def is_tech_related(title, summary):
    text = (title + " " + summary).lower()
    return any(keyword in text for keyword in TECH_KEYWORDS)

def parse_rss_feeds():
    articles = []
    seen_ids = set()
    for source, url in RSS_FEEDS.items():
        print(f"  📡 Fetching: {source}")
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:15]:
                title   = entry.get("title", "").strip()
                summary = entry.get("summary", "").strip()
                link    = entry.get("link", "").strip()
                if not title or not link:
                    continue
                article_id = make_id(title)
                if article_id in seen_ids:
                    continue
                seen_ids.add(article_id)
                if not is_tech_related(title, summary):
                    continue
                articles.append({
                    "id":           article_id,
                    "source":       source,
                    "title":        title,
                    "summary":      summary[:500],
                    "url":          link,
                    "collected_at": datetime.now(timezone.utc).isoformat()
                })
        except Exception as e:
            print(f"  ⚠️  Failed {source}: {e}")
    return articles

def fetch_newsapi(articles):
    api_key = os.getenv("NEWSAPI_KEY")
    if not api_key:
        print("  ⚠️  NEWSAPI_KEY not set, skipping")
        return articles
    try:
        response = requests.get(
            "https://newsapi.org/v2/top-headlines",
            params={"category": "technology", "language": "en", "pageSize": 20, "apiKey": api_key},
            timeout=10
        )
        data = response.json()
        seen_ids = {a["id"] for a in articles}
        for item in data.get("articles", []):
            title   = (item.get("title") or "").strip()
            summary = (item.get("description") or "").strip()
            link    = (item.get("url") or "").strip()
            if not title or not link or "[Removed]" in title:
                continue
            article_id = make_id(title)
            if article_id in seen_ids:
                continue
            seen_ids.add(article_id)
            if not is_tech_related(title, summary):
                continue
            articles.append({
                "id":           article_id,
                "source":       "NewsAPI",
                "title":        title,
                "summary":      summary[:500],
                "url":          link,
                "collected_at": datetime.now(timezone.utc).isoformat()
            })
        print("  ✅ NewsAPI articles added")
    except Exception as e:
        print(f"  ⚠️  NewsAPI failed: {e}")
    return articles

def save_articles(articles):
    os.makedirs("data/raw_news", exist_ok=True)
    today    = datetime.now().strftime("%Y-%m-%d")
    filepath = f"data/raw_news/news_{today}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)
    return filepath

def collect_news():
    print("\n🚀 Starting News Collector...")
    print("─" * 40)
    print("\n[1/3] Fetching RSS feeds...")
    articles = parse_rss_feeds()
    print(f"  ✅ Collected: {len(articles)} articles")
    print("\n[2/3] Fetching from NewsAPI...")
    articles = fetch_newsapi(articles)
    print(f"  ✅ Total: {len(articles)} articles")
    print("\n[3/3] Saving to file...")
    filepath = save_articles(articles)
    print(f"  ✅ Saved: {filepath}")
    print("\n" + "─" * 40)
    print(f"✅ Done! {len(articles)} articles collected.")
    print("─" * 40)
    return articles
