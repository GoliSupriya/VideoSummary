import json
import os
import yt_dlp as ytdl
import subprocess

def extract_clip(video_path, start_time, duration, clip_filename):
    """Extract video clip based on timestamps."""
    command = [
        'ffmpeg', '-i', video_path, '-ss', str(start_time), '-t', str(duration),
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
        '-c:a', 'aac', '-b:a', '192k', '-strict', 'experimental',
        '-y',  # Overwrite existing file if needed
        clip_filename
    ]
    process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if process.returncode != 0:
        print(f"❌ FFmpeg error: {process.stderr.decode()}")
    else:
        print(f"✅ Clip saved: {clip_filename}")

def combine_clips(clip_filenames, output_filename):
    """Combine multiple video clips into one using concat demuxer."""
    if not clip_filenames:
        print("❌ No clips to combine.")
        return

    # Ensure `data/` directory exists
    if not os.path.exists("data"):
        os.makedirs("data")

    list_file = os.path.join("data", "clip_list.txt")  # Fixed path

    # Write absolute paths to avoid FFmpeg issues
    with open(list_file, "w") as f:
        for clip in clip_filenames:
            clip_path = os.path.abspath(clip)  # Convert to absolute path
            if os.path.exists(clip_path):
                f.write(f"file '{clip_path}'\n")
            else:
                print(f"❌ Missing clip: {clip_path}")
                return  

    command = [
        "ffmpeg", "-f", "concat", "-safe", "0", "-i", list_file,
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "192k", "-strict", "experimental",
        "-y",  # Overwrite existing file
        output_filename
    ]

    process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if process.returncode != 0:
        print(f"❌ FFmpeg error while combining: {process.stderr.decode()}")
    else:
        print(f"✅ Combined video saved as {output_filename}")

    os.remove(list_file)  # Cleanup

def generate_summarized_video(video, timestamps, output_video_filename="output_video.mp4"):
    """Create summarized video using extracted clips."""
    video_path = os.path.join(video)  # Fixed path

    clip_filenames = []
    if not os.path.exists("data"):
        os.makedirs("data")

    for i, timestamp in enumerate(timestamps):
        try:
            start_time = timestamp['start_time']
            end_time = timestamp['end_time']
            duration = end_time - start_time
            clip_filename = os.path.join("data", f"clip_{i}.mp4")  # Fixed path
            extract_clip(video_path, start_time, duration, clip_filename)
            clip_filenames.append(clip_filename)
        except Exception as e:
            print(f"❌ Error processing timestamp {timestamp}: {e}")

    combine_clips(clip_filenames, output_video_filename)

    for clip_filename in clip_filenames:
        os.remove(clip_filename)
    os.remove(video_path)
    print(f"✅ Summarized video created: {output_video_filename}")
    return output_video_filename
