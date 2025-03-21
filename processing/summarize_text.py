import os
from transformers import pipeline, AutoTokenizer
from .download_audio import extract_audio_from_video, transcribe_audio

# Load pre-trained BART summarization model
model_name = "facebook/bart-large-cnn"
summarizer = pipeline("summarization", model=model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Get the model's max token limit
MAX_TOKEN_LIMIT = tokenizer.model_max_length

# Function to split large text into smaller chunks
def split_text(text, max_chunk_size=MAX_TOKEN_LIMIT):  
    sentences = text.split('. ')  
    chunks, current_chunk = [], ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_chunk_size:
            current_chunk += sentence + ". "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

# Function to summarize large text
def summarize_text(transcript_text):
    if not transcript_text.strip():
        print("⚠️ Transcript is empty. Skipping summarization.")
        return "No valid text found to summarize."

    chunks = split_text(transcript_text)  
    summaries = []

    print(f"🔹 Splitting text into {len(chunks)} chunks...")

    for i, chunk in enumerate(chunks):  
        input_length = len(chunk.split())
        max_length = max(50, int(input_length * 0.6))  
        min_length = max(20, int(max_length * 0.5))

        print(f"📝 Summarizing chunk {i+1}/{len(chunks)}...")

        try:
            summary = summarizer(chunk, max_length=max_length, min_length=min_length, do_sample=False)[0]['summary_text']
            summaries.append(summary)
        except Exception as e:
            print(f"❌ Error summarizing chunk {i+1}: {e}")
            summaries.append("[Summary error]")

    return " ".join(summaries)

# Main function to process a video
def summarizeText(video):
    if not video or not os.path.exists(video):
        raise FileNotFoundError("❌ Invalid or missing video file.")

    print("🎬 Processing video:", video)

    # Step 1: Extract audio
    wav_file = extract_audio_from_video(video)
    if not wav_file or not os.path.exists(wav_file):
        raise FileNotFoundError("❌ Failed to extract audio.")

    # Step 2: Transcribe the extracted audio
    transcript_file = transcribe_audio(wav_file)
    if not transcript_file or not os.path.exists(transcript_file):
        raise FileNotFoundError("❌ Failed to transcribe audio.")

    print(f"✅ Transcript saved to: {transcript_file}")

    # Step 3: Read the transcript
    with open(transcript_file, "r", encoding="utf-8") as file:
        transcript_text = file.read().strip()

    if not transcript_text:
        return "⚠️ Transcript is empty. No summary generated."

    # Step 4: Generate summary
    summary = summarize_text(transcript_text)

    # Step 5: Save the summary
    summary_dir = "data"
    os.makedirs(summary_dir, exist_ok=True)  
    summary_file = os.path.join(summary_dir, "summary.txt")

    with open(summary_file, "w", encoding="utf-8") as file:
        file.write(summary)

    print(f"✅ Summary saved to: {summary_file}")
    os.remove("data/extracted_audio.wav")
    os.remove("data/summary.txt")
    os.remove("data/transcript.txt")
    os.remove("downloads/video.mp4")
    return summary_file
