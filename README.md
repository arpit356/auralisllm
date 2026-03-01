# Auralis: Private AI Meeting Assistant

Auralis is an offline, **Local LLM Digital Twin** that captures decisions and tasks while answering questions from your private dataset. It ensures 100% data privacy by running entirely on your machine.

---

## 🚀 Key Features

*   **100% Offline**: No external APIs or internet required for daily use.
*   **Intelligent RAG**: Searches through thousands of local documents (`.txt`) in milliseconds.
*   **Structured Memory**: Automatically extracts and categorizes:
    *   ✅ **Decisions** (e.g., budget approvals, project name changes).
    *   ✅ **Action Items** (e.g., tasks assigned to specific people).
    *   ✅ **Questions** asked during the meeting.
*   **Persistent Logging**: Automatically saves meeting transcripts to the dataset for long-term memory.
*   **Auralis API**: A built-in FastAPI server to connect the AI brain to any frontend or mobile app.

---

## 🛠️ Installation & Setup

### 1. Prerequisites
*   **Install [Ollama](https://ollama.com)**: This manages the local LLM.
*   **Python 3.10+**: (Recommended: 3.13).

### 2. Install Dependencies
Run this command in your terminal:
```bash
pip install -r requirements.txt
```

### 3. Setup the AI Brain
Download the specific 1.5B model (optimized for standard RAM):
```bash
python model_downloader.py
```

### 4. Ingest Your Knowledge Base
Drop your meeting notes, policies, or research files into the `dataset/` folder, then run:
```bash
python local_knowledge_base.py
```

---

## 🏃 How to Run

### Option A: The Complete Integrated Assistant
To run the full simulation with persona, structured memory, and RAG in one script:
```bash
python a3_auralis_system_complete.py
```

### Option B: Run as a Service (API)
To expose Auralis to a web frontend or other apps:
1. Start the API:
   ```bash
   python auralis_api.py
   ```
2. Test the connection in another terminal:
   ```bash
   python test_api.py
   ```

---

## 📡 API Endpoints

The API runs by default on `http://localhost:8000`.

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/process` | `POST` | Process a transcript line (returns AI action + speech). |
| `/memory` | `GET` | Fetch all decisions, tasks, and questions. |
| `/memory` | `DELETE` | Reset memory for a new meeting. |
| `/health` | `GET` | Basic health check for the brain. |

---

## 💡 Tips for High Accuracy

Since Auralis uses a small, efficient model (1.5B), follow these "Trigger Word" patterns for near 100% accuracy:
*   **Decisions**: "We have decided to..." or "Decision: [Your point]."
*   **Tasks**: "Alice, please do [task]." or "Action for Charlie: [task]."
*   **Direct Questions**: "Auralis, what is the main goal?"

---

## 📂 Project Structure

*   `a3_auralis_system_complete.py`: The main integrated AI orchestrator.
*   `auralis_api.py`: FastAPI implementation for external integration.
*   `local_knowledge_base.py`: Handles vector storage (ChromaDB) and RAG search.
*   `dataset/`: Folder for your private knowledge base and meeting history.
*   `requirements.txt`: List of all Python libraries needed.

---

## ⚠️ Troubleshooting

*   **Port 8000 Conflict**: If the API fails to start, run this in PowerShell:
    `Stop-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess -Force`
*   **Model Not Found**: Ensure Ollama is running in your system tray before starting the scripts.
