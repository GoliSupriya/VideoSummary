import whisper

def transcribe_audio(audio_path):
    """Convert audio to text using OpenAI Whisper."""
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result["text"]

if __name__ == "__main__":
    audio_file = "data/temp_audio.wav"
    transcription = transcribe_audio(audio_file)
    with open("data/transcription.txt", "w") as f:
        f.write(transcription)
    print("Transcription complete! Check 'data/transcription.txt'")
