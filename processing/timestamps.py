import spacy
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from whisper import load_model
import json
import os

# Load optimized models once (avoid reloading multiple times)
nlp = spacy.load("en_core_web_sm")  # Smaller SpaCy model
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')  # Faster sentence embedding model
whisper_model = load_model("tiny")  # Load Whisper once globally

def get_matching_timestamps(transcribed_text, summarized_text, transcribed_timestamps, similarity_threshold=0.5):
    """Find timestamps for summarized sentences based on transcribed text similarity."""


    
    transcribed_sentences = [sent.text.strip() for sent in nlp(transcribed_text).sents]
    summarized_sentences = [sent.text.strip() for sent in nlp(summarized_text).sents]

    # Batch process embeddings (Faster)
    transcribed_embeddings = model.encode(transcribed_sentences, batch_size=8, convert_to_numpy=True)
    summarized_embeddings = model.encode(summarized_sentences, batch_size=8, convert_to_numpy=True)

    matching_timestamps = []
    seen_sentences = set()

    for i, summarized_sentence in enumerate(summarized_sentences):
        # Compute cosine similarity efficiently
        similarities = cosine_similarity([summarized_embeddings[i]], transcribed_embeddings)[0]
        best_match_index = np.argmax(similarities)
        best_match_score = similarities[best_match_index]

        # Ensure sentence is unique and score is above threshold
        if best_match_score > similarity_threshold and transcribed_sentences[best_match_index] not in seen_sentences:
            seen_sentences.add(transcribed_sentences[best_match_index])

            # Check if timestamps exist (avoid index errors)
            if best_match_index < len(transcribed_timestamps):
                matching_timestamps.append({
                    "start_time": transcribed_timestamps[best_match_index][0],
                    "end_time": transcribed_timestamps[best_match_index][1],
                    "matched_sentence": transcribed_sentences[best_match_index],
                    "similarity_score": round(float(best_match_score), 4)
                })

    # Sort timestamps to ensure chronological order
    matching_timestamps.sort(key=lambda x: x["start_time"])
    return matching_timestamps


def transcribe_audio(audio_path):
    """Optimized Whisper transcription."""
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    result = whisper_model.transcribe(audio_path)  # No word timestamps (faster)
    text = result.get('text', '')  # Get transcribed text
    timestamps = [(segment['start'], segment['end']) for segment in result.get('segments', [])]
    
    return text, timestamps


def generate_timestamps_based_on_summary(audio_path, summarized_text, output_path="data/timestamps.json"):
    """Generate timestamps based on summarized text and save as JSON."""
    transcribed_text, transcribed_timestamps = transcribe_audio(audio_path)
    matching_timestamps = get_matching_timestamps(transcribed_text, summarized_text, transcribed_timestamps)

    # Ensure the directory exists before saving
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(matching_timestamps, f, indent=2)

    return matching_timestamps

