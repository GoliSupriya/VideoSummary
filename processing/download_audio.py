import os
import torch
from pydub import AudioSegment
from whisper import load_model

def extract_audio_from_video(video_file):
    """Extracts and preprocesses audio from a video file quickly."""
    if not video_file or not os.path.exists(video_file):
        print(f"Error: Video file {video_file} not found.")
        return None
    
    output_audio = "data/extracted_audio.wav"
    
    # Create directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    try:
        print(f"[Step 1] Extracting audio from {video_file}")
        audio = AudioSegment.from_file(video_file)

        # Convert to mono & set frame rate for faster transcription
        audio = audio.set_channels(1).set_frame_rate(16000)

        # Export as WAV
        audio.export(output_audio, format="wav")
        print("[Step 1] Audio extraction successful!")
        
        return output_audio
    except Exception as e:
        print(f"Error during audio extraction: {e}")
        return None

def transcribe_audio(audio_path):
    """Transcribes audio using Whisper with GPU acceleration (if available)."""
    if not audio_path or not os.path.exists(audio_path):
        print(f"Error: Audio file {audio_path} not found.")
        return None
    
    try:
        # Auto-detect GPU
        device = "cuda" if torch.cuda.is_available() else "cpu"

        # Load the optimized Whisper model
        model = load_model("tiny", device=device)

        print(f"[Step 2] Transcribing audio: {audio_path} using {device}")
        
        # Transcribe with optimizations
        result = model.transcribe(audio_path, language="en", temperature=0, fp16=True if device == "cuda" else False)

        print("[Step 2] Transcription successful!")

        # Save transcript to a text file
        transcript_text = result["text"]
        transcript_path = "data/transcript.txt"
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(transcript_text)

        print(f"[Step 3] Transcript saved to {transcript_path}")

        return transcript_path
    except Exception as e:
        print(f"Error during transcription: {e}")
        return None