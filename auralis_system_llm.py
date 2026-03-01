import json
import datetime
import os
import ollama
from local_knowledge_base import search_knowledge_base

# --- 1. Define Model ---
MODEL_NAME = "qwen2.5:1.5b"

# --- 2. Configuration ---
auralis_config = {
    "persona": {
        "role": "AI Digital Twin for meeting assistance",
        "traits": ["helpful", "professional", "concise", "proactive"],
        "nuances": "Prioritizes user's explicit commands; provides insights without interruption unless critical."
    },
    "communication_style": {
        "verbosity_level": "concise",
        "formality_level": "semi-formal"
    }
}

# --- 3. Helper functions ---
def _get_current_timestamp():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds') + 'Z'

# These are simplified mock functions. They construct the raw JSON output 
# that an external system (like a frontend UI) would expect.
def generate_speak_output(text: str) -> dict:
    return {"mode": "speak", "content": {"text": text}}

def generate_silent_output(log: str) -> dict:
    return {"mode": "silent", "content": {"log_message": log}}


# --- 4. The Real AI Logic via Ollama ---

def ask_local_llm(prompt: str, json_format=False) -> str:
    """Helper to query the local Ollama instance."""
    
    try:
        # If we need JSON, we tell Ollama to enforce it
        format_kwarg = "json" if json_format else ""
        
        # We use the generate endpoint for direct prompting
        response = ollama.generate(
            model=MODEL_NAME, 
            prompt=prompt,
            format=format_kwarg
        )
        return response['response'].strip()
        
    except Exception as e:
        print(f"Error querying Ollama LLM: {e}")
        # Helpful message if they forgot to run Ollama in the background
        if "connect" in str(e).lower() or "connection" in str(e).lower():
            print("\nCRITICAL: Is the Ollama app running on your computer?")
        return "{}" if json_format else "I encountered an error processing that request locally."


def save_to_meeting_memory(speaker: str, transcript: str):
    """
    Appends the current transcript line to a 'meeting_memory.txt' file 
    inside the dataset folder so Auralis can learn from it in future sessions.
    """
    if not os.path.exists("dataset"):
        os.makedirs("dataset")
        
    log_file = os.path.join("dataset", "current_meeting_memory.txt")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {speaker}: {transcript}\n")

def process_meeting_input_with_llm(meeting_context: dict) -> dict:
    """
    Uses the local Ollama LLM and RAG dataset to decide Auralis's next action.
    """
    transcript = meeting_context.get("transcript", "")
    speaker = meeting_context.get("speaker", "Unknown")

    if not transcript.strip():
        return {"action_type": "silent", "content": {"log_message": "Silence, waiting for input."}}

    # NEW: Automatically save this transcript line to our long-term dataset memory
    save_to_meeting_memory(speaker, transcript)

    # Improvement: Extract high-level keywords for better RAG retrieval
    # Instead of searching for the whole sentence, we pick out the key terms.
    search_query = transcript
    for word in ["auralis", "summarize", "review", "dataset", "please", "could", "you"]:
        search_query = search_query.lower().replace(word, "").strip()

    # 1. RAG Search: Check our local dataset for relevant information
    # We now get 5 results to ensure the target is found among the noise.
    rag_context = search_knowledge_base(search_query, n_results=5)
    
    # 2. Build the LLM Prompt
    system_prompt = f"""You are Auralis, an AI Meeting Assistant.
Role: {auralis_config['persona']['role']}
Traits: {', '.join(auralis_config['persona']['traits'])}

Analyze the latest meeting transcript.
Speaker: {speaker}
Transcript: "{transcript}"

Below is background reference material from our internal dataset. 
If the user asks for a 'goal' or 'summary', USE THIS INFORMATION to provide a concrete answer:
---
{rag_context if rag_context else "No specific background reference found."}
---

Decide what action to take. You MUST output a valid JSON object with the exact following structure:
{{
  "action_type": "memory_add_action_item" | "memory_add_decision" | "speak" | "silent",
  "content": {{
     "text": "Your helpful response. If you found the 'goal' in the context, describe it now.",
     "extracted_data": "Any important extracted data (populated if action_type is a memory action)"
  }}
}}

IF the context contains a 'main goal' or 'policy', summarize it clearly in the 'text' field.
"""
    
    # 3. Call the Local LLM
    print(f"\n[Auralis Thinking...] Searching through {len(os.listdir('dataset'))} records...")
    llm_response = ask_local_llm(system_prompt, json_format=True)
    
    try:
        # 4. Parse Decision
        decision_data = json.loads(llm_response)
        
        # Safety fallback
        if "action_type" not in decision_data:
            decision_data["action_type"] = "silent"
            
        action_type = decision_data["action_type"]
        content = decision_data.get("content", {})
        
        if action_type == "speak":
            return generate_speak_output(content.get("text", "Understood."))
        else:
            return generate_silent_output(f"LLM decided to log: {action_type} - {content}")
            
    except json.JSONDecodeError:
        print(f"Warning: Failed to parse LLM JSON output: {llm_response}")
        return generate_silent_output("LLM provided invalid JSON formatting.")


# --- 5. Quick Simulation ---
if __name__ == "__main__":
    print("\n--- Starting Local Ollama Auralis Test ---")
    
    test_context = {
        "speaker": "Alice",
        "transcript": "Auralis, review the dataset and summarize our main goal based on what we discussed earlier."
    }
    
    print(f"\nAlice says: {test_context['transcript']}")
    
    # Execute the simulation
    result = process_meeting_input_with_llm(test_context)
    
    print("\nAuralis Action Output:")
    print(json.dumps(result, indent=2))
