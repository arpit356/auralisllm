import ollama
import sys

# We use Llama 3.2 (3 Billion parameters) for high IQ reasoning.
# It requires ~2.5-3 GB of RAM, fitting within your hardware limits
# while significantly improving conversation accuracy.
MODEL_NAME = "llama3.2:3b" 

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
