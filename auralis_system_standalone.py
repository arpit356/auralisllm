
import json
import datetime

# --- 1. Define auralis_config dictionary directly in the script ---
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
    },
    "knowledge_base_structure": {
        "categories": ["meeting context", "user history", "domain-specific data"],
        "integration_concept": "Contextual retrieval and synthesis for relevant responses."
    },
    "purpose": [
        "facilitate communication by summarizing and clarifying",
        "capture key information (questions, decisions, action items)",
        "provide timely insights based on tracked memory and persona knowledge"
    ]
}

# --- 2. Helper functions for timestamp ---
def _get_current_timestamp():
    """Helper function to get current ISO 8601 formatted timestamp."""
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds') + 'Z'

# --- 3. Output generation functions ---
def generate_speak_output(text_to_speak: str) -> dict:
    """
    Generates a dictionary conforming to the 'speak' JSON schema.
    """
    return {
        "mode": "speak",
        "content": {
            "text": text_to_speak
        }
    }

def generate_silent_output(log_message: str, data_update_dict: dict = None) -> dict:
    """
    Generates a dictionary conforming to the 'silent' JSON schema.
    """
    content = {
        "log_message": log_message
    }
    if data_update_dict:
        content["data_update"] = data_update_dict
    return {
        "mode": "silent",
        "content": content
    }

def generate_flag_output(reason: str, severity: str, timestamp: str = None) -> dict:
    """
    Generates a dictionary conforming to the 'flag' JSON schema.
    Severity can be 'low', 'medium', or 'high'.
    """
    if timestamp is None:
        timestamp = _get_current_timestamp()

    return {
        "mode": "flag",
        "content": {
            "reason": reason,
            "severity": severity,
            "timestamp": timestamp
        }
    }

def generate_final_report_output(
    meeting_summary: str,
    questions_list: list,
    key_points_list: list,
    decisions_list: list,
    action_items_list: list
) -> dict:
    """
    Generates a dictionary conforming to the 'final_report' JSON schema.
    """
    return {
        "mode": "final_report",
        "content": {
            "meeting_summary": meeting_summary,
            "questions": questions_list,
            "key_points": key_points_list,
            "decisions": decisions_list,
            "action_items": action_items_list
        }
    }

# --- 4. Meeting memory and its management functions ---
meeting_memory_global = {
    "questions": [],
    "key_points": [],
    "decisions": [],
    "action_items": []
}

def initialize_meeting_memory():
    global meeting_memory_global
    meeting_memory_global = {
        "questions": [],
        "key_points": [],
        "decisions": [],
        "action_items": []
    }

def add_question(question_text: str, asked_by: str, timestamp: str = None, answer: str = None):
    """
    Appends a new question dictionary to meeting_memory_global["questions"].
    """
    if timestamp is None:
        timestamp = _get_current_timestamp()
    question_entry = {
        "question": question_text,
        "asked_by": asked_by,
        "timestamp": timestamp,
        "answer": answer
    }
    meeting_memory_global["questions"].append(question_entry)
    print(f"Added question: {question_text}")

def update_question_answer(question_index: int, answer_text: str):
    """
    Updates the 'answer' field of an existing question in meeting_memory_global["questions"].
    """
    if 0 <= question_index < len(meeting_memory_global["questions"]):
        meeting_memory_global["questions"][question_index]["answer"] = answer_text
        print(f"Updated answer for question {question_index}: {answer_text}")
    else:
        print(f"Error: Question index {question_index} out of bounds.")

def add_key_point(point_text: str, timestamp: str = None):
    """
    Appends a new key point dictionary to meeting_memory_global["key_points"].
    """
    if timestamp is None:
        timestamp = _get_current_timestamp()
    key_point_entry = {
        "point": point_text,
        "timestamp": timestamp
    }
    meeting_memory_global["key_points"].append(key_point_entry)
    print(f"Added key point: {point_text}")

def add_decision(decision_text: str, made_by: str, timestamp: str = None):
    """
    Appends a new decision dictionary to meeting_memory_global["decisions"].
    """
    if timestamp is None:
        timestamp = _get_current_timestamp()
    decision_entry = {
        "decision": decision_text,
        "made_by": made_by,
        "timestamp": timestamp
    }
    meeting_memory_global["decisions"].append(decision_entry)
    print(f"Added decision: {decision_text}")

def add_action_item(item_text: str, assigned_to: str, due_date: str = None, status: str = "pending", timestamp: str = None):
    """
    Appends a new action item dictionary to meeting_memory_global["action_items"].
    """
    if timestamp is None:
        timestamp = _get_current_timestamp()
    action_item_entry = {
        "item": item_text,
        "assigned_to": assigned_to,
        "due_date": due_date, # YYYY-MM-DD format expected
        "status": status,
        "timestamp": timestamp
    }
    meeting_memory_global["action_items"].append(action_item_entry)
    print(f"Added action item: {item_text}")

def update_action_item_status(item_index: int, new_status: str):
    """
    Updates the status of an existing action item in meeting_memory_global["action_items"].
    """
    if 0 <= item_index < len(meeting_memory_global["action_items"]):
        meeting_memory_global["action_items"][item_index]["status"] = new_status
        print(f"Updated status for action item {item_index} to {new_status}")
    else:
        print(f"Error: Action item index {item_index} out of bounds.")

# --- 5. Mock versions of decision logic functions ---

def mock_check_meeting_state(meeting_context: dict) -> dict:
    """
    Mock: Determines if Auralis should consider speaking. More permissive for testing memory.
    Returns a state and a proposed_action (e.g., 'consider_speaking', 'remain_silent').
    """
    transcript = meeting_context.get("transcript", "").lower()
    speaker = meeting_context.get("speaker", "").lower()
    silence_duration = meeting_context.get("silence_duration", 0)

    if "auralis" in transcript and speaker != "auralis":
        return {"state": "direct_address", "proposed_action": "consider_speaking"}
    if silence_duration > 2.0: # A reasonable pause
        return {"state": "pause", "proposed_action": "consider_speaking"}
    if "critical" in transcript or "urgent" in transcript: # Allow interjection for critical topics
        return {"state": "critical_topic", "proposed_action": "consider_speaking"}

    # Default to considering speaking for now to allow other logic to run for demonstration
    return {"state": "general_discussion", "proposed_action": "consider_speaking"}

def mock_determine_response_necessity(meeting_context: dict, persona_data: dict) -> dict:
    """
    Mock: Assesses if a response is genuinely required or beneficial.
    Returns necessity (boolean) and potential_response (string).
    """
    transcript = meeting_context.get("transcript", "").lower()
    speaker = meeting_context.get("speaker", "").lower()
    state_check_result = meeting_context.get("state_check_result", {})

    # Even if state is 'remain_silent', we might still need to process for memory or other internal states
    # This mock focuses on speaking necessity.

    if state_check_result.get("proposed_action") == "remain_silent":
        return {"necessity": False, "potential_response": ""}

    if "auralis" in transcript and speaker != "auralis":
        if "summarize" in transcript:
            return {"necessity": True, "potential_response": "I can provide a summary. What period would you like me to cover?"}
        if "question" in transcript:
            return {"necessity": True, "potential_response": "How may I assist you with that question?"}
        else:
            return {"necessity": True, "potential_response": "Yes, how may I assist?"}

    if state_check_result.get("state") == "pause":
        # If there's a pause and Auralis has something proactive to say (e.g., a pending item)
        # For this mock, we'll keep it simple: no proactive speaking unless directly addressed.
        pass

    if state_check_result.get("state") == "critical_topic":
        return {"necessity": True, "potential_response": "I've noted the critical topic. Is there anything I can add or clarify?"}

    return {"necessity": False, "potential_response": ""}

def mock_speaking_guidelines(meeting_context: dict, proposed_response: str, persona_data: dict) -> str:
    """
    Mock: Refines how Auralis will speak based on persona guidelines.
    Returns the refined response.
    """
    if not proposed_response:
        return ""

    verbosity = persona_data["communication_style"]["verbosity_level"]
    formality = persona_data["communication_style"]["formality_level"]

    refined_response = proposed_response
    if verbosity == "concise":
        refined_response = refined_response.replace("I can provide a summary. What period would you like me to cover?", "Summary request noted.")
        refined_response = refined_response.replace("How may I assist you with that question?", "How can I help with the question?")
        refined_response = refined_response.replace("I've noted the critical topic. Is there anything I can add or clarify?", "Critical topic noted. Assistance needed?")
        refined_response = refined_response.replace("Yes, how may I assist?", "How may I assist?")

    if formality == "formal":
        # For this mock, we'll just add a simple prefix for formality
        refined_response = f"Greetings. {refined_response}" if not refined_response.startswith("Greetings") else refined_response

    return f"[Auralis]: {refined_response}"

def mock_identity_safety_check(meeting_context: dict, proposed_output: str, persona_data: dict) -> dict:
    """
    Mock: Ensures output adheres to safety and ethical guidelines.
    Returns a dict with 'safe_output' (str) and 'safety_status' (str).
    """
    if "confidential report" in meeting_context.get("transcript", "").lower():
        return {"safe_output": "I cannot disclose confidential reports due to privacy protocols.", "safety_status": "blocked_privacy"}
    if "personal gossip" in proposed_output.lower(): # Check for persona avoid_topics
        return {"safe_output": "I must respectfully decline to engage in that topic.", "safety_status": "blocked_ethical"}

    return {"safe_output": proposed_output, "safety_status": "safe"}

# --- 6. Main orchestration functions ---
def decide_auralis_action(meeting_context: dict, persona_data: dict) -> dict:
    """
    Orchestrates the mock decision logic steps to determine Auralis's action.
    Returns an action type and content for output generators or memory tracking.
    Prioritizes memory capture.
    """
    transcript = meeting_context.get("transcript", "").lower()
    speaker = meeting_context.get("speaker", "").lower()

    # --- Priority 1: Memory Capture (always attempt this first) ---
    if "question:" in transcript and "auralis" not in transcript: # Ensure it's not a question *to* Auralis
        q_text = transcript.split("question:", 1)[1].strip()
        return {"action_type": "memory_add_question", "content": {"question_text": q_text, "asked_by": speaker.title()}}
    elif "decision:" in transcript:
        d_text = transcript.split("decision:", 1)[1].strip()
        return {"action_type": "memory_add_decision", "content": {"decision_text": d_text, "made_by": speaker.title()}}
    elif "action item:" in transcript or ("action for" in transcript and "auralis" not in transcript): # Avoid interpreting 'action for Auralis' as an item for others
        ai_text = transcript.split("action item:", 1)[1].strip() if "action item:" in transcript else transcript.split("action for", 1)[1].strip()
        assigned_to_match = [p for p in ['alice', 'bob', 'charlie'] if p in ai_text] # Simple assignment
        assigned_to = assigned_to_match[0].title() if assigned_to_match else "Unassigned"
        return {"action_type": "memory_add_action_item", "content": {"item_text": ai_text, "assigned_to": assigned_to}}
    elif "key point:" in transcript:
        kp_text = transcript.split("key point:", 1)[1].strip()
        return {"action_type": "memory_add_key_point", "content": {"point_text": kp_text}}

    # --- Priority 2: Speaking Actions (only if no memory capture action was taken) ---

    # Step 1: Check Meeting State
    state_check_result = mock_check_meeting_state(meeting_context)
    meeting_context["state_check_result"] = state_check_result # Pass result to next steps

    # Step 2: Determine Response Necessity (if state is conducive)
    if state_check_result["proposed_action"] == "consider_speaking":
        necessity_result = mock_determine_response_necessity(meeting_context, persona_data)
        proposed_response = necessity_result["potential_response"]

        if necessity_result["necessity"]:
            # Step 3: Speaking Guidelines
            final_response_text = mock_speaking_guidelines(meeting_context, proposed_response, persona_data)

            # Step 4: Identity Safety (applied to the proposed final response)
            safety_check_result = mock_identity_safety_check(meeting_context, final_response_text, persona_data)

            if safety_check_result["safety_status"].startswith("blocked"):
                return {"action_type": "flag", "content": {"reason": safety_check_result["safe_output"], "severity": "high"}}

            if safety_check_result["safe_output"] and safety_check_result["safe_output"] != "[Auralis]: Greetings. ": # Check for empty response after guidelines
                return {"action_type": "speak", "content": {"text": safety_check_result["safe_output"]}}

    return {"action_type": "silent", "content": {"log_message": "Processed input, no explicit vocal or memory action required."}}


def simulate_meeting_turn(meeting_context: dict, persona_data: dict, current_meeting_memory: dict) -> dict:
    """
    Simulates a single turn in a meeting, orchestrating Auralis's decision and output.
    Returns the Auralis's output dictionary and updates the meeting memory in place.
    """
    # IMPORTANT: The current_meeting_memory parameter is ignored here as memory is managed by global `meeting_memory_global`.
    # In a class-based implementation, this would be a member variable.

    auralis_decision = decide_auralis_action(meeting_context, persona_data)
    output_dict = {}

    action_type = auralis_decision["action_type"]
    content = auralis_decision["content"]

    current_timestamp = _get_current_timestamp()

    if action_type == "speak":
        output_dict = generate_speak_output(content["text"])
    elif action_type == "silent":
        output_dict = generate_silent_output(content["log_message"])
    elif action_type == "flag":
        output_dict = generate_flag_output(content["reason"], content.get("severity", "medium"), current_timestamp)
    elif action_type == "memory_add_question":
        add_question(content["question_text"], content["asked_by"], current_timestamp)
        output_dict = generate_silent_output(f"Question added to memory: {content['question_text']}")
    elif action_type == "memory_add_decision":
        add_decision(content["decision_text"], content["made_by"], current_timestamp)
        output_dict = generate_silent_output(f"Decision added to memory: {content['decision_text']}")
    elif action_type == "memory_add_action_item":
        add_action_item(content["item_text"], content["assigned_to"], status="pending", timestamp=current_timestamp)
        output_dict = generate_silent_output(f"Action item added to memory: {content['item_text']}")
    elif action_type == "memory_add_key_point":
        add_key_point(content["point_text"], current_timestamp)
        output_dict = generate_silent_output(f"Key point added to memory: {content['point_text']}")
    else:
        output_dict = generate_silent_output("Unknown action type received.")

    return output_dict

print("auralis_system_standalone.py created successfully!")

# --- 7. Executable Simulation Block ---
if __name__ == "__main__":
    print("\n--- Starting Auralis Standalone Simulation ---")

    # Mock meeting contexts for demonstration
    mock_meeting_contexts = [
        {
            "speaker": "Alice",
            "transcript": "Hello Auralis, could you please summarize the last discussion point?",
            "current_turn_duration": 5,
            "silence_duration": 0.5
        },
        {
            "speaker": "Bob",
            "transcript": "I think the key point here is: Budget optimization is crucial for Q3.",
            "current_turn_duration": 7,
            "silence_duration": 0.1
        },
        {
            "speaker": "Charlie",
            "transcript": "So the decision: We will proceed with the new vendor for infrastructure.",
            "current_turn_duration": 8,
            "silence_duration": 0.2
        },
        {
            "speaker": "Alice",
            "transcript": "Great. Action item: Bob, please draft the contract by next Friday.",
            "current_turn_duration": 10,
            "silence_duration": 0.3
        },
        {
            "speaker": "Bob",
            "transcript": "Question: What are the next steps for implementation, Alice?",
            "current_turn_duration": 6,
            "silence_duration": 0.1
        },
        {
            "speaker": "System",
            "transcript": "", # Simulating a period of silence
            "current_turn_duration": 0,
            "silence_duration": 3.0
        },
        {
            "speaker": "Alice",
            "transcript": "Auralis, what are the privacy implications of this feature?",
            "current_turn_duration": 7,
            "silence_duration": 0.2
        },
        {
            "speaker": "Bob",
            "transcript": "We have a critical security flaw detected! This needs urgent attention.",
            "current_turn_duration": 4,
            "silence_duration": 0.1
        },
        {
            "speaker": "Alice",
            "transcript": "I need Auralis to give me the confidential report from yesterday.",
            "current_turn_duration": 8,
            "silence_duration": 0.5
        },
        {
            "speaker": "Charlie",
            "transcript": "Key point: User feedback has been overwhelmingly positive for the new UI concept.",
            "current_turn_duration": 9,
            "silence_duration": 0.4
        },
        {
            "speaker": "System",
            "transcript": "", # Another silent period
            "current_turn_duration": 0,
            "silence_duration": 4.0
        },
        {
            "speaker": "Bob",
            "transcript": "Action for Charlie: Review the UI concept and schedule a follow-up meeting.",
            "current_turn_duration": 12,
            "silence_duration": 0.2
        }
    ]

    # Re-initialize meeting_memory for a clean simulation
    initialize_meeting_memory()
    print("Meeting memory re-initialized for simulation.")

    print("\n--- Simulating Live Meeting Turns ---")
    for i, context in enumerate(mock_meeting_contexts):
        print(f"\nTurn {i+1} - Speaker: {context['speaker']}, Transcript: '{context['transcript']}'")

        # Simulate a turn and get Auralis's output
        auralis_output = simulate_meeting_turn(context, auralis_config, meeting_memory_global)

        print("Auralis Output:")
        print(json.dumps(auralis_output, indent=2))

        print("Current Meeting Memory:")
        print(json.dumps(meeting_memory_global, indent=2))

    # Generate Final Report at the conclusion of all turns
    print("\n--- Generating Final Report for Simulated Meeting ---")
    final_report_summary = "Comprehensive summary of the simulated meeting, including all captured points, decisions, questions, and action items." # In a real system, this would be dynamically generated by an NLP model.
    final_report_output = generate_final_report_output(
        final_report_summary,
        meeting_memory_global["questions"],
        meeting_memory_global["key_points"],
        meeting_memory_global["decisions"],
        meeting_memory_global["action_items"]
    )
    print(json.dumps(final_report_output, indent=2))

    print("\n--- Auralis Standalone Simulation Complete ---")
