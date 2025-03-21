import librosa
import numpy as np
from pydub import AudioSegment
from .download_audio import extract_audio_from_video  # Assuming this is for extracting audio from video

# Step 1: Audio Analysis using Librosa
def analyze_audio(file_path):
    # Load audio file using librosa
    y, sr = librosa.load(file_path)

    # Calculate the energy of the audio signal
    energy = librosa.feature.rms(y=y)[0]

    # Detect silent parts based on energy threshold
    silence_threshold = np.mean(energy) * 0.5  # Customize this threshold
    non_silent_intervals = librosa.effects.split(y, top_db=20)

    # Extract dominant pitch (frequency)
    pitches, magnitudes = librosa.core.piptrack(y=y, sr=sr)
    pitch = [pitches[magnitudes[:, i].argmax()] for i in range(magnitudes.shape[1])]

    return energy, non_silent_intervals, pitch

# Step 2: Audio Clipping based on Energy and Silence Detection
def clip_audio(file_path, non_silent_intervals):
    # Load audio file using PyDub (for easy manipulation)
    audio = AudioSegment.from_file(file_path)

    # Create a new audio segment by combining non-silent intervals
    clips = []
    for start, end in non_silent_intervals:
        clip = audio[start:end]  # Extract audio between start and end points
        clips.append(clip)

    # Combine all clips into one
    final_clip = sum(clips)

    # Export the clipped audio to a new file
    final_clip.export("clipped_audio.wav", format="wav")
    print("Clipped audio saved as 'clipped_audio.wav'")

    return final_clip  # Return the final clipped audio

# Step 3: Putting It All Together
def create_audio_summary(file_path):
    # Step 1: Analyze audio for pitch, energy, and silence
    energy, non_silent_intervals, pitch = analyze_audio(file_path)

    # Step 2: Clip the audio based on silence and energy thresholds
    output = clip_audio(file_path, non_silent_intervals)

    # Step 3: Save the final clipped audio as a file and return the file path
    output_file_path = "clipped_audio.wav"
    output.export(output_file_path, format="wav")
    
    # Return the path to the saved audio file
    return output_file_path  # Return the path to the saved file
