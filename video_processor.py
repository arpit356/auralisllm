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
    Returns a dictionary with transcription metadata.
    """
    if not os.path.exists(video_path):
        print(f"Error: File {video_path} not found.")
        return None

    if not os.path.exists(DATASET_DIR):
        os.makedirs(DATASET_DIR)

    file_size_mb = os.path.getsize(video_path) / (1024 * 1024)

    print(f"Loading Whisper model ({WHISPER_MODEL_SIZE})...")
    model = WhisperModel(WHISPER_MODEL_SIZE, device="cpu", compute_type="int8")

    print(f"Transcribing: {os.path.basename(video_path)} ({file_size_mb:.2f} MB)")
    print("This may take some time depending on video length...")
    
    segments, info = model.transcribe(video_path, beam_size=5)

    full_text = ""
    word_count = 0
    duration = info.duration
    
    for segment in segments:
        full_text += f"[{segment.start:.2f}s -> {segment.end:.2f}s]: {segment.text}\n"
        word_count += len(segment.text.split())

    # Save to dataset folder for RAG indexing
    filename = os.path.basename(video_path)
    output_filename = f"transcript_{filename}.txt"
    output_path = os.path.join(DATASET_DIR, output_filename)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"--- Transcript for {filename} ---\n")
        f.write(f"Processed on: {datetime.datetime.now()}\n")
        f.write(f"Duration: {duration:.2f}s | Word Count: {word_count}\n\n")
        f.write(full_text)

    video_info = {
        "filename": filename,
        "duration_seconds": round(duration, 2),
        "word_count": word_count,
        "file_size_mb": round(file_size_mb, 2),
        "output_path": output_path
    }

    print("\n--- Video Transcription Summary ---")
    print(f"File: {video_info['filename']}")
    print(f"Duration: {video_info['duration_seconds']}s")
    print(f"Words: {video_info['word_count']}")
    print(f"Output: {video_info['output_path']}")
    print("----------------------------------\n")
    
    return video_info

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python video_processor.py <path_to_video_or_audio>")
    else:
        transcribe_video(sys.argv[1])
