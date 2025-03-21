import os
import yt_dlp

# Folder to save downloaded videos
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def download_progress_hook(d):
    """Displays real-time download progress."""
    if d['status'] == 'downloading':
        print(f"\rDownloading: {d['_percent_str']} at {d['_speed_str']}", end='', flush=True)
    elif d['status'] == 'finished':
        print("\nDownload complete. Processing video...")

def download_youtube_video(video_url: str):
    """Downloads a YouTube video quickly and saves it as 'video.mp4'."""
    try:
        clean_url = video_url.split("&")[0].strip()  # Remove unnecessary parameters

        ydl_opts = {
            'format': 'bv*+ba/b',  # Best video + best audio
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, 'video.mp4'),  # Always save as 'video.mp4'
            'noplaylist': True,  # Download only the video, not a playlist
            'merge_output_format': 'mp4',  # Ensure MP4 output
            'concurrent-fragments': 10,  # Parallel downloads for speed
            'fragment-retries': 10,  # Retry on fragment failures
            'retries': 5,  # Retry failed downloads
            'socket_timeout': 20,  # Prevent timeouts
            'progress_hooks': [download_progress_hook],  # Show progress
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"\nDownloading video from: {clean_url}")
            ydl.download([clean_url])

        video_path = os.path.join(DOWNLOAD_FOLDER, 'video.mp4')
        print(f"\n✅ Download complete! Saved as: {video_path}")
        return video_path  

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


