# Auralis Deployment Guide

Since Auralis is a local-first LLM system, deployment is different from standard web apps. You have three main options depending on your privacy and budget needs.

---

## 🏗️ Deployment Options

### 1. Private Server (Recommended for Privacy)
If you have a dedicated PC or a Server in your office, this is the best way to keep data 100% private.
*   **Specs**: 8GB+ RAM, 4-core CPU (GPU highly recommended for the 3B model).
*   **Operating System**: Linux (Ubuntu 22.04) or Windows 11.
*   **Setup**: Simply follow the `README.md` steps on that machine and expose port `8000` to your internal network.

### 2. Cloud Virtual Machine (AWS, Google Cloud, Azure)
Best for making the API accessible globally to your team.
*   **Recommended Instance**: 
    *   **AWS**: `g4dn.xlarge` (includes an NVIDIA T4 GPU).
    *   **Google Cloud**: `n1-standard-4` with 1x NVIDIA T4.
*   **Setup**:
    1.  Install Docker and NVIDIA Container Toolkit.
    2.  Run Ollama as a Docker container.
    3.  Run Auralis as a separate container (see `Dockerfile`).

### 3. GPU Cloud (RunPod, Lambda Labs)
Best for high performance at the lowest cost.
*   Use a "Pod" with an NVIDIA RTX 3060 or better.
*   These providers often have Ollama pre-installed.

---

## 🐳 Docker Deployment (Containerization)

The easiest way to run Auralis is using **Docker Compose**.

### 1. One-Click Start
Run this command in the project folder:
```bash
docker-compose up -d
```
This will automatically:
*   Start **Ollama** (The Brain).
*   Start **Auralis API** (The Service).
*   Connect them together.

### 2. Pulling the Model
After the containers are running, you may need to pull the model once:
```bash
docker exec -it auralis-brain ollama pull llama3.2:3b
```

---

## 🔒 Production Security

Your API is now secured with **API Key Authentication**.

*   **Header Name**: `X-API-KEY`
*   **Default Key**: `auralis_secret_key_2026`

**To change your key**: 
Edit the `API_KEY` variable at the top of [auralis_api.py](auralis_api.py).

**Example Request**:
```bash
curl -X POST http://localhost:8000/process \
     -H "X-API-KEY: auralis_secret_key_2026" \
     -H "Content-Type: application/json" \
     -d '{"speaker": "Alice", "transcript": "Auralis, record this decision."}'
```

---

## 📈 Scaling for Many Users
If multiple people use Auralis at the same time:
*   **Ollama Memory**: Increase the timeout for the model to stay in memory.
*   **GPU RAM**: Use a model with **Quantization (4-bit)** to save VRAM.
*   **Vector DB**: ChromaDB is fast for 50k+ docs, but for millions of docs, consider migrating to **Weaviate** or **Pinecone**.
