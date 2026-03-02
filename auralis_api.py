from fastapi import FastAPI, HTTPException, Depends, Security, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from typing import Optional, Dict, List
import json
import os
import shutil
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from a3_auralis_system_complete import process_meeting_turn, meeting_memory_global
from video_processor import transcribe_video

# Load environment variables from .env file (works locally and in Docker)
load_dotenv()

# --- Configuration & Security ---
# API Key is loaded from the environment. Set AURALIS_API_KEY in your .env file.
API_KEY = os.environ.get("AURALIS_API_KEY", "auralis_secret_key_2026")
API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(header_value: str = Security(api_key_header)):
    if header_value == API_KEY:
        return header_value
    raise HTTPException(status_code=401, detail="Invalid or missing API Key")

app = FastAPI(title="Auralis Local AI API", version="1.2.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def landing_page():
    return """
    <html>
        <head>
            <title>Auralis AI Assistant</title>
            <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;600&display=swap" rel="stylesheet">
            <style>
                body { 
                    margin: 0; padding: 0; 
                    background: radial-gradient(circle at top right, #1a1a2e, #16213e);
                    color: white; font-family: 'Outfit', sans-serif;
                    height: 100vh; display: flex; align-items: center; justify-content: center;
                }
                .container { 
                    text-align: center; padding: 40px; 
                    background: rgba(255, 255, 255, 0.05);
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 24px;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                }
                h1 { font-size: 3rem; margin-bottom: 10px; background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
                p { color: #8fa1c4; font-size: 1.2rem; }
                .status { 
                    display: inline-block; margin-top: 20px; padding: 8px 20px; 
                    background: rgba(0, 255, 127, 0.1); border: 1px solid #00ff7f; 
                    color: #00ff7f; border-radius: 50px; font-weight: 600;
                    box-shadow: 0 0 15px rgba(0, 255, 127, 0.2);
                }
                .pulse { 
                    display: inline-block; width: 10px; height: 10px; 
                    background: #00ff7f; border-radius: 50%; margin-right: 8px;
                    animation: pulse 1.5s infinite;
                }
                @keyframes pulse { 0% { transform: scale(0.95); opacity: 1; } 50% { transform: scale(1.1); opacity: 0.7; } 100% { transform: scale(0.95); opacity: 1; } }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Auralis LLM</h1>
                <p>Private AI Meeting Assistant is currently</p>
                <div class="status"><span class="pulse"></span> RUNNING (v1.2.0)</div>
                <div style="margin-top: 30px; font-size: 0.9rem; color: #5c6c8c;">Endpoint: <code>http://localhost:8000/process</code></div>
            </div>
        </body>
    </html>
    """

# --- Data Models ---
class MeetingTurnRequest(BaseModel):
    speaker: str
    transcript: str

# --- Endpoints ---

@app.get("/health")
async def health_check():
    return {"status": "online", "model": "llama3.2:3b", "engine": "Ollama/RAG+Whisper", "security": "enabled"}

@app.post("/process")
async def process_turn(request: MeetingTurnRequest, api_key: str = Depends(get_api_key)):
    try:
        result = process_meeting_turn(request.speaker, request.transcript)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transcribe")
async def upload_video(file: UploadFile = File(...), api_key: str = Depends(get_api_key)):
    """Uploads and transcribes a video/audio file."""
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    
    file_path = os.path.join("uploads", file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        result = transcribe_video(file_path)
        return {"status": "success", "metadata": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/memory")
async def get_memory(api_key: str = Depends(get_api_key)):
    return meeting_memory_global

@app.delete("/memory")
async def reset_memory(api_key: str = Depends(get_api_key)):
    global meeting_memory_global
    for key in meeting_memory_global:
        meeting_memory_global[key] = []
    return {"status": "memory_reset"}

def kill_port_process(port: int):
    """Aggressively finds and kills any process using the specified port."""
    import subprocess
    import time
    print(f"[*] Checking if port {port} is clear...")
    try:
        for _ in range(3): # Try 3 times to be sure
            cmd = f'netstat -ano | findstr :{port}'
            output = subprocess.check_output(cmd, shell=True).decode()
            found = False
            for line in output.strip().split('\n'):
                if "LISTENING" in line and f":{port}" in line:
                    pid = line.strip().split()[-1]
                    # Don't kill ourselves if we somehow match
                    if int(pid) != os.getpid():
                        print(f"[!] Target found! Killing process {pid} blocking port {port}...")
                        subprocess.run(f'taskkill /F /PID {pid}', shell=True, capture_output=True)
                        found = True
            if not found:
                break
            time.sleep(1) # Wait for OS to release the port
    except Exception:
        pass # Port is likely already clear

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    
    # PERMANENT FIX: Automatically clear the port if blocked
    if port == 8000:
        kill_port_process(8000)
        
    uvicorn.run(app, host="0.0.0.0", port=port)
