import os
import json
from .download_audio import extract_audio_from_video, transcribe_audio
from .summary_text import summarize_text_with_t5
from .timestamps import generate_timestamps_based_on_summary
from .generatevideo import generate_summarized_video
from .download import download_youtube_video

def summarize(video):
    if not video:
        print("Failed to download the video.")
        exit(1)  # Stop execution if video download fails

    # Step 1: Extract audio
    wav_file = extract_audio_from_video(video)

    if not wav_file:
        print("Failed to extract audio from the video.")
        exit(1)  # Stop execution if audio extraction fails

    # Step 2: Transcribe the extracted audio
    transcript_file = transcribe_audio(wav_file)

    if not transcript_file:
        print("Failed to transcribe audio.")
        exit(1)  # Stop execution if transcription fails

    print(f"Transcript saved to: {transcript_file}")

    with open("data/transcript.txt", "r", encoding="utf-8") as file:
        transcript_text = file.read()

    # Step 3: Summarize text
    print("[Step 3] Summarizing transcript...")
    summary = summarize_text_with_t5(transcript_text)

    if not summary:
        print("Failed to summarize the transcript.")
        exit(1)



    print(summary)

    # Step 4: Match timestamps
    print("[Step 4] Finding matching timestamps...")
    timestamps = generate_timestamps_based_on_summary(wav_file,summary)

    if not timestamps:
        print("Failed to generate timestamps.")
        exit(1)

    # Save timestamps
    with open("data/timestamps.json", "w") as f:
        json.dump(timestamps, f, indent=2)

    # Step 5: Generate summarized video
    print("[Step 5] Generating summarized video...")

    output=generate_summarized_video(video, timestamps)
    return output






