import os
from faster_whisper import WhisperModel
import datetime

# --- Configuration ---
DATASET_DIR = "dataset"
# Models: "tiny", "base", "small", "medium", "large-v3"
# "base" is fast and fairly accurate for CPU.
WHISPER_MODEL_SIZE = "base"

def transcribe_video(video_path):
    """
    Transcribes a video or audio file and saves the result to the dataset folder.
    """
    if not os.path.exists(video_path):
        print(f"Error: File {video_path} not found.")
        return None

    if not os.path.exists(DATASET_DIR):
        os.makedirs(DATASET_DIR)

    print(f"Loading Whisper model ({WHISPER_MODEL_SIZE})...")
    # Using 'cpu' as default, device="cuda" if user has a GPU
    model = WhisperModel(WHISPER_MODEL_SIZE, device="cpu", compute_type="int8")

    print(f"Transcribing: {video_path}")
    print("This may take some time depending on video length...")
    
    segments, info = model.transcribe(video_path, beam_size=5)

    full_text = ""
    for segment in segments:
        full_text += f"[{segment.start:.2f}s -> {segment.end:.2f}s]: {segment.text}\n"

    # Save to dataset folder for RAG indexing
    filename = os.path.basename(video_path)
    output_filename = f"transcript_{filename}.txt"
    output_path = os.path.join(DATASET_DIR, output_filename)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"--- Transcript for {filename} ---\n")
        f.write(f"Processed on: {datetime.datetime.now()}\n\n")
        f.write(full_text)

    print(f"✅ Transcription complete! Saved to: {output_path}")
    return output_path

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python video_processor.py <path_to_video_or_audio>")
    else:
        transcribe_video(sys.argv[1])
