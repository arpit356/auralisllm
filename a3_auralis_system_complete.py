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
        print(f"✅ Added to {category}: {json.dumps(data, indent=2)}")

# --- 3. Persistent Memory Logging (Saving to Text File) ---
def save_to_meeting_memory_file(speaker: str, transcript: str):
    """Appends transcript to a text file for future RAG retrieval."""
    if not os.path.exists("dataset"):
        os.makedirs("dataset")
    log_file = os.path.join("dataset", "current_meeting_memory.txt")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{_get_current_timestamp()}] {speaker}: {transcript}\n")

# --- 4. Local LLM Integration (Ollama) ---
MODEL_NAME = "qwen2.5:1.5b"

def ask_local_llm(prompt: str, json_format=True) -> str:
    """Sends a prompt to the local Ollama instance."""
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    if json_format:
        payload["format"] = "json"
        
    try:
        response = httpx.post(url, json=payload, timeout=60.0)
        return response.json().get("response", "{}")
    except Exception as e:
        print(f"Error querying Ollama: {e}")
        return "{}"

# --- 5. Main Decision Logic ---
def process_meeting_turn(speaker: str, transcript: str) -> dict:
    """Uses LLM to decide on actions and update memory."""
    if not transcript.strip():
        return {"mode": "silent", "content": "Silence noted."}

    # Save to text log for future RAG
    save_to_meeting_memory_file(speaker, transcript)

    # 1. Deterministic Check: Force RAG+Speak for direct Auralis summary requests
    lower_t = transcript.lower()
    if "auralis" in lower_t and ("summarize" in lower_t or "goal" in lower_t):
        print(f"\n[Auralis] Detected direct request for summary. Performing RAG...")
        rag_context = search_knowledge_base("main goal privacy policy", n_results=5)
        prompt = f"Background: {rag_context}\n\nTask: Auralis, summarize our main goal for {speaker} using ONLY the background info above."
        vocal_response = ask_local_llm(prompt, json_format=False)
        return {"mode": "speak", "content": vocal_response}

    # 2. General AI Decision for Memory Actions
    system_prompt = f"""
You are Auralis, an AI Meeting Assistant.
Persona: {auralis_config['persona']['role']}

EXAMPLES:
- "Decision: Budget approved" -> {{"action": "add_decision", "data": {{"item": "Budget approved", "made_by": "Speaker"}}}}
- "Alice, do X" -> {{"action": "add_action_item", "data": {{"item": "Do X", "assigned_to": "Alice"}}}}
- "Who did this?" -> {{"action": "add_question", "data": {{"item": "Who did this?", "asked_by": "Speaker"}}}}

TRANSCRIPT: "{speaker}: {transcript}"

TASK:
Categorize this transcript line. 
- If Decision -> "add_decision"
- If Task/Action Item -> "add_action_item"
- If Question -> "add_question"
- Else -> "silent"

Return ONLY valid JSON:
{{
  "action": "add_question" | "add_decision" | "add_action_item" | "silent",
  "data": {{ "item": "The specific text to remember", "assigned_to": "Name", "made_by": "{speaker}", "asked_by": "{speaker}" }}
}}
"""
    
    decision_json = ask_local_llm(system_prompt, json_format=True)
    try:
        decision = json.loads(decision_json)
        action = decision.get("action", "silent")
        data = decision.get("data", {})
        
        # Dispatch to memory
        if action == "add_question":
            add_memory_item("questions", data)
        elif action == "add_decision":
            add_memory_item("decisions", data)
        elif action == "add_action_item":
            add_memory_item("action_items", data)
            
        return {"mode": "silent", "content": f"Action taken: {action}"}
        
    except Exception as e:
        return {"mode": "silent", "content": f"Decision error: {e}"}

# --- 6. Full Simulation Loop ---
if __name__ == "__main__":
    print(f"--- Starting Auralis Integrated Simulation (Model: {MODEL_NAME}) ---")
    
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
