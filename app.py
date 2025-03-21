from flask import Flask, render_template, request, send_file, url_for, redirect, abort
from werkzeug.utils import secure_filename
from processing.download import download_youtube_video
import os
from processing.summarize_video import summarize
from processing.summarize_text import summarizeText
from processing.summarize_audio import extract_audio_from_video,create_audio_summary

app = Flask(__name__)

# Folder paths
DOWNLOAD_FOLDER = "downloads"
UPLOAD_FOLDER = "uploads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)  # Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["DOWNLOAD_FOLDER"] = DOWNLOAD_FOLDER
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    youtube_url = request.form.get('youtubeUrl')  # Get YouTube URL
    summarization_type = request.form.get('summarization_type')  # Get summarization type
    video_file = request.files.get('videoFile')  # Get uploaded video file

    print("📩 Received Form Data:", request.form)
    print("📂 Received Files:", request.files)

    video_path = None  # Initialize video_path

    if youtube_url:
        print("🎥 Downloading YouTube video...")
        video_path = download_youtube_video(youtube_url)  # Returns full path

        if not video_path or not os.path.exists(video_path):
            print("❌ Error: Video download failed!")
            return "Failed to download video.", 400

        print(f"✅ Video downloaded successfully: {video_path}")

    elif video_file and video_file.filename:
        filename = secure_filename(video_file.filename)  # Secure filename
        video_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        video_file.save(video_path)  # Save uploaded file
        print(f"✅ Video file saved at: {video_path}")

    else:
        print("⚠️ No valid input received.")
        return "❌ Error: Provide either a YouTube URL or upload a video file.", 400  # Return proper error response

    # Ensure summarization type is provided
    if not summarization_type:
        return "⚠️ Please select a summarization type.", 400

    if summarization_type == 'summarized_video':
        print("📽️ Starting video summarization...")
        output_path = summarize(video_path)

        

        print(f"✅ Summarized video saved at: {output_path}")
        output_filename = os.path.basename(output_path)
        return redirect(url_for('display_video', filename=output_filename))
    if summarization_type == 'summarized_text':
        print("📽️ Starting video summarization...")
        output_path = summarizeText(video_path)

        

        print(f"✅ Summarized video saved at: {output_path}")
        output_filename = os.path.basename(output_path)
        return redirect(url_for('display_text', filename=output_filename))
    if summarization_type == 'summarized_audio':
        print("📽️ Starting video summarization...")
        output=extract_audio_from_video(video_path)
        output_path=create_audio_summary(output)
       
        

        print(f"✅ Summarized audio saved at: {output_path}")
        output_filename = os.path.basename(output_path)
        return redirect(url_for('display_audio', filename=output_filename))

    return "❌ Error: Invalid summarization type.", 400  # Handle invalid summarization types
VIDEO_FILE = "output_video.mp4"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/video')
def display_video():
    return render_template('video.html', video_filename=VIDEO_FILE)

@app.route('/serve_video')
def serve_video():
    video_path = os.path.join(BASE_DIR, VIDEO_FILE)  # Use BASE_DIR instead of DOWNLOAD_FOLDER

    if os.path.exists(video_path):
        return send_file(video_path, mimetype="video/mp4", as_attachment=False)

    print("❌ Error: Video file not found:", video_path)
    return abort(404, "Video not found.")

TEXT_FILE = "summary.txt"
@app.route('/text')
def display_text():

    text_path = os.path.join(BASE_DIR, TEXT_FILE)

    if os.path.exists(text_path):
        with open(text_path, "r", encoding="utf-8") as file:
            summary_text = file.read()  # Read the content of the file
        
        return render_template('text.html', summary_text=summary_text, text_filename=TEXT_FILE)

@app.route('/serve_text')
def serve_text():
    text_path = os.path.join(BASE_DIR, TEXT_FILE)

    if os.path.exists(text_path):
        return send_file(text_path, mimetype="text/plain", as_attachment=False)

    print("❌ Error: Text file not found:", text_path)
    return abort(404, "Text file not found.")

AUDIO_FILE = 'clipped_audio.wav'
@app.route('/audio')
def display_audio():
    audio_path = os.path.join(BASE_DIR, AUDIO_FILE)

    if os.path.exists(audio_path):
        # You can include an audio player in your HTML page
        return render_template('audio.html', audio_filename=AUDIO_FILE)

    print("❌ Error: Audio file not found:", audio_path)
    return abort(404, "Audio file not found.")

@app.route('/serve_audio')
def serve_audio():
    audio_path = os.path.join(BASE_DIR, AUDIO_FILE)

    if os.path.exists(audio_path):
        return send_file(audio_path, mimetype="audio/mp3", as_attachment=False)

    print("❌ Error: Audio file not found:", audio_path)
    return abort(404, "Audio file not found.")



if __name__ == '__main__':
    app.run(debug=True)

