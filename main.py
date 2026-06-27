import os
import sys
sys.path.insert(0, os.getcwd())

from src.news_collector import collect_news
from src.data_cleaner import clean_and_rank
from src.viral_scorer import run_viral_scorer
from src.script_generator import generate_final_script
from src.narration_generator import generate_narration
from src.video_generator import create_video

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import json

def upload_to_youtube(video_path, article):
    token_data = {
        "refresh_token": os.getenv("YOUTUBE_REFRESH_TOKEN"),
        "token_uri":     "https://oauth2.googleapis.com/token",
        "client_id":     os.getenv("YOUTUBE_CLIENT_ID"),
        "client_secret": os.getenv("YOUTUBE_CLIENT_SECRET")
    }

    creds   = Credentials(token=None, **token_data)
    youtube = build("youtube", "v3", credentials=creds)

    title       = article["title"][:80] + " #Shorts"
    description = f"{article['title']}\n\n{article['summary']}\n\n#AI #Tech #Shorts"
    media       = MediaFileUpload(video_path, chunksize=-1, resumable=True)

    response = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title":       title,
                "description": description,
                "tags":        ["AI", "Tech", "Shorts", "Technology", "News"],
                "categoryId":  "28"
            },
            "status": {
                "privacyStatus":           "public",
                "selfDeclaredMadeForKids": False
            }
        },
        media_body=media
    ).execute()

    video_id = response.get("id")
    return f"https://youtube.com/shorts/{video_id}"

def main():
    print("=" * 50)
    print("  REC AUTO VIDEO - AI Branding Engine")
    print("=" * 50)

    print("\n[1/6] Collecting news...")
    articles = collect_news()

    print("\n[2/6] Cleaning and ranking...")
    ranked = clean_and_rank()

    print("\n[3/6] Scoring viral potential...")
    best_article, best_score = run_viral_scorer(ranked)

    if not best_article:
        print("❌ No good topic found today. Stopping.")
        return

    print("\n[4/6] Generating script...")
    final_script = generate_final_script(best_article)

    print("\n[5/6] Generating narration and video...")
    narration_path = generate_narration(final_script)
    video_path     = create_video(narration_path, final_script, os.getenv("PEXELS_API_KEY"))

    print("\n[6/6] Uploading to YouTube...")
    url = upload_to_youtube(video_path, best_article)
    print(f"✅ Video live: {url}")

    print("\n" + "=" * 50)
    print("  ✅ PIPELINE COMPLETE!")
    print("=" * 50)

if __name__ == "__main__":
    main()
