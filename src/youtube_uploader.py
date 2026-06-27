import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_youtube_service():
    flow = InstalledAppFlow.from_client_secrets_file(
        "client_secrets.json", SCOPES
    )
    credentials = flow.run_local_server(port=8080)
    youtube = build("youtube", "v3", credentials=credentials)
    return youtube, credentials

def upload_video(video_path, title, description):
    print("\n📤 Starting YouTube Uploader...")
    print("─" * 40)

    youtube, credentials = get_youtube_service()

    request_body = {
        "snippet": {
            "title":       title[:100],
            "description": description,
            "tags":        ["AI", "Tech", "Shorts", "Technology", "News"],
            "categoryId":  "28"
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)

    print("  Uploading video...")
    response = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media
    ).execute()

    video_id  = response.get("id")
    video_url = f"https://youtube.com/shorts/{video_id}"

    print(f"  ✅ Uploaded successfully!")
    print(f"  🔗 URL: {video_url}")
    print("─" * 40)
    print("✅ Done!")
    print("─" * 40)

    return video_url
