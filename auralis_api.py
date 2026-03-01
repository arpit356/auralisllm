from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
import json
from fastapi.middleware.cors import CORSMiddleware
from a3_auralis_system_complete import process_meeting_turn, meeting_memory_global

app = FastAPI(title="Auralis Local AI API", version="1.0.0")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Models ---
class MeetingTurnRequest(BaseModel):
    speaker: str
    transcript: str

class ActionContent(BaseModel):
    mode: str
    content: str

# --- Endpoints ---

@app.get("/health")
async def health_check():
    return {"status": "online", "model": "qwen2.5:1.5b", "engine": "Ollama/RAG"}

@app.post("/process", response_model=Dict)
async def process_turn(request: MeetingTurnRequest):
    """
    Processes a single meeting turn using the Auralis LLM and RAG system.
    Returns the action (speak/silent) and updates internal memory.
    """
    try:
        result = process_meeting_turn(request.speaker, request.transcript)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memory")
async def get_memory():
    """Returns the current structured meeting memory (questions, decisions, tasks)."""
    return meeting_memory_global

@app.delete("/memory")
async def reset_memory():
    """Resets the meeting memory for a fresh session."""
    global meeting_memory_global
    meeting_memory_global["questions"] = []
    meeting_memory_global["key_points"] = []
    meeting_memory_global["decisions"] = []
    meeting_memory_global["action_items"] = []
    return {"status": "memory_reset"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
