import ollama
import sys

# We use Qwen 2.5 (1.5 Billion parameters). This model only requires
# ~1.2 GB of RAM, meaning it will run comfortably on almost any laptop
# without triggering out-of-memory errors, while still understanding JSON.
MODEL_NAME = "qwen2.5:1.5b" 

def download_local_model():
    """
    Downloads the specified model via Ollama.
    """
    print(f"Ensuring {MODEL_NAME} is downloaded via Ollama...")
    print("This will take a few minutes if you haven't downloaded it before.")
    
    try:
         # This command asks the local Ollama server to fetch the model
        ollama.pull(MODEL_NAME)
        print(f"\n✅ Successfully pulled '{MODEL_NAME}' into your local Ollama environment.")
        print("You are ready to run Auralis offline.")
    except Exception as e:
        print(f"\n❌ Error pulling model: {e}")
        print("\nCRITICAL: Make sure you have downloaded and installed the Ollama application.")
        print("1. Go to https://ollama.com/")
        print("2. Download and install it.")
        print("3. Ensure the Ollama app is running in your taskbar/menu bar.")
        print("4. Try running this script again.")

if __name__ == "__main__":
    download_local_model()
