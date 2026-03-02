import json
import datetime
import os
import httpx
from local_knowledge_base import search_knowledge_base

# --- 1. Auralis Configuration (Rich Persona from Standalone) ---
auralis_config = {
    "persona": {
        "role": "AI Digital Twin for meeting assistance",
        "traits": ["helpful", "professional", "concise", "proactive"],
        "nuances": "Prioritizes user's explicit commands; provides insights without interruption unless critical."
    },
    "communication_style": {
        "verbosity_level": "concise",
        "formality_level": "semi-formal",
        "tone": "neutral",
        "turn_taking": "wait for explicit pause or direct address; interject if critical"
    },
    "user_preferences": {
        "reporting_format": "JSON",
        "prioritized_topics": ["decisions", "action items", "unresolved questions"],
        "avoid_topics": ["personal gossip", "sensitive company secrets without explicit clearance"],
        "interaction_frequency": "moderate"
    }
}

# --- 2. Global Meeting Memory (Tracking Logic from Standalone) ---
meeting_memory_global = {
    "questions": [],
    "key_points": [],
    "decisions": [],
    "action_items": []
}

def _get_current_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def add_memory_item(category: str, data: dict):
    """Adds a structured item to the meeting memory."""
    if category in meeting_memory_global:
        data["timestamp"] = _get_current_timestamp()
        meeting_memory_global[category].append(data)
        print(f"[Memory] Added to {category}: {json.dumps(data, indent=2)}")

# --- 3. Persistent Memory Logging (Saving to Text File) ---
def save_to_meeting_memory_file(speaker: str, transcript: str):
    """Appends transcript to a text file for future RAG retrieval."""
    if not os.path.exists("dataset"):
        os.makedirs("dataset")
    log_file = os.path.join("dataset", "current_meeting_memory.txt")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{_get_current_timestamp()}] {speaker}: {transcript}\n")

# --- 4. Local LLM Integration (Ollama) ---
CORE_MODEL = "llama3.2:3b"      # For deep reasoning/answers
FAST_MODEL = "llama3.2:1b"      # For fast & reliable categorization
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")

def ask_local_llm(prompt: str, json_format=True, max_tokens=100, model=CORE_MODEL) -> str:
    """Sends a prompt to Ollama with latency-optimized options."""
    url = f"{OLLAMA_HOST}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": max_tokens,  # Limit output length for speed
            "temperature": 0,           # Deterministic for speed
            "num_thread": 4              # Optimize for CPU
        }
    }
    if json_format:
        payload["format"] = "json"
        
    try:
        response = httpx.post(url, json=payload, timeout=120.0)
        text = response.json().get("response", "").strip()
        return text if text else ("{}" if json_format else "I'm listening.")
    except Exception as e:
        print(f"Error querying Ollama ({model}): {e}")
        return "{}" if json_format else "I'm having trouble connecting."

# --- 5. Main Decision Logic ---
def process_meeting_turn(speaker: str, transcript: str) -> dict:
    """Uses LLM to decide on actions and update memory."""
    if not transcript.strip():
        return {"mode": "silent", "content": "Silence noted."}

    # Save to text log for future RAG
    save_to_meeting_memory_file(speaker, transcript)

    # 1. Deterministic Check: Force RAG+Speak for direct Auralis questions/requests
    lower_t = transcript.lower()
    if "auralis" in lower_t:
        is_question = "?" in lower_t or any(q in lower_t for q in ["what", "how", "who", "where", "why", "summarize", "goal", "can you"])
        if is_question:
            print(f"\n[Auralis] Detected direct question/task: '{transcript}'")
            # Log it first
            add_memory_item("questions", {"item": transcript, "asked_by": speaker})
            
            # Perform RAG lookup
            rag_context = search_knowledge_base(transcript, n_results=5)
            prompt = f"Background: {rag_context}\n\nTask: Auralis, answer this: '{transcript}' based on the background. If the info isn't there, use your persona knowledge. Persona: {auralis_config['persona']['role']}"
            vocal_response = ask_local_llm(prompt, json_format=False)
            return {"mode": "speak", "content": vocal_response}

    # 2. Fast-Path Heuristic: Keywords (Deteriministic & Instant)
    if any(k in lower_t for k in ["decision:", "decided:", "approved", "confirmed", "agreed"]):
        item = transcript.split(":", 1)[1].strip() if ":" in transcript else transcript
        data = {"item": item, "made_by": speaker}
        add_memory_item("decisions", data)
        return {"mode": "silent", "content": "Acknowledged: Decision recorded."}
    
    if any(k in lower_t for k in ["task:", "action:", "todo:", "please", "assigned", "responsible"]):
        item = transcript.split(":", 1)[1].strip() if ":" in transcript else transcript
        data = {"item": item, "made_by": speaker}
        add_memory_item("action_items", data)
        return {"mode": "silent", "content": "Noted: Action item saved."}

    # 3. Skip AI for short chitchat (< 4 words)
    words = lower_t.split()
    if len(words) < 4 and not any(k in lower_t for k in ["?", "who", "when", "how", "why"]):
        return {"mode": "silent", "content": "Noted."}

    # 4. Optimized AI Decision (Using TinyLlama for a bit more 'IQ' than 0.5B but still sub-3s)
    system_prompt = f"""Task: Categorize this meeting line.
Transcript: "{speaker}: {transcript}"

Is this a:
A) Action Item (Task to do)
B) Decision (Something decided/approved)
C) Question (Something asked)
D) Silent (General talk, thanks, hello)

Return valid JSON: {{"action": "add_action_item" | "add_decision" | "add_question" | "silent", "data": {{"item": "summary", "made_by": "{speaker}"}}}}"""
    
    # Use TINYLLAMA for better 1B categorization (fast and reliable)
    decision_json = ask_local_llm(system_prompt, json_format=True, max_tokens=60, model="tinyllama")
    try:
        decision = json.loads(decision_json)
        action = decision.get("action", "silent")
        data = decision.get("data", {})
        
        if action == "add_question":
            add_memory_item("questions", data)
            return {"mode": "silent", "content": f"Question saved."}
        elif action == "add_decision":
            add_memory_item("decisions", data)
            return {"mode": "silent", "content": f"Decision recorded."}
        elif action == "add_action_item":
            add_memory_item("action_items", data)
            return {"mode": "silent", "content": f"Action item saved."}
            
        return {"mode": "silent", "content": "Noted."}
    except:
        return {"mode": "silent", "content": "Listening."}

# --- 6. Full Simulation Loop ---
if __name__ == "__main__":
    print(f"--- Starting Auralis Integrated Simulation (Model: {CORE_MODEL}) ---")
    
    turns = [
        ("Alice", "Hello everyone. Auralis, please note: Budget for Q3 is approved for $50k."),
        ("Bob", "I have a question: Who is managing the vendor relationship?"),
        ("Alice", "Charlie, you are in charge of that. Please draft the contract by Monday."),
        ("Charlie", "Got it. Key point: We need to use the new security protocols for all data transfers."),
        ("Alice", "Auralis, review the dataset and summarize our main goal.")
    ]
    
    for speaker, transcript in turns:
        print(f"\n[Turn] {speaker}: {transcript}")
        result = process_meeting_turn(speaker, transcript)
        print(f"[Auralis] {result['mode'].upper()}: {result['content']}")

    print("\n--- Final Meeting Memory State ---")
    print(json.dumps(meeting_memory_global, indent=2))
