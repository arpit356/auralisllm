# ☁️ Auralis AI — Cloud Deployment Guide (Public Access)

This guide deploys Auralis to a **DigitalOcean Droplet** so anyone can
access your API using your API Key.

---

## Prerequisites
- A [DigitalOcean](https://digitalocean.com) account (or any Linux VPS)
- Your Auralis project folder
- Git installed on your machine

---

## 🛡️ Step 1: Set Your API Key (.env file)

Before deploying, open the `.env` file in your project and change the key:

```
AURALIS_API_KEY=my_super_secret_key_2026
```

> ⚠️ **WARNING**: Never share your `.env` file. Never commit it to GitHub.
> The `.gitignore` file already protects it automatically.

---

## 🖥️ Step 2: Create a Cloud Server

1. Go to **DigitalOcean** → **Create** → **Droplet**
2. Choose:
   - **OS**: Ubuntu 22.04 LTS
   - **Plan**: Basic — **8GB RAM / 4 CPU** (~$48/mo)  ← required for AI models
   - **Region**: Choose closest to your users
3. Add your SSH key or create a root password
4. Click **Create Droplet**

---

## 🔗 Step 3: Connect to Your Server

```bash
ssh root@YOUR_SERVER_IP
```

---

## 📦 Step 4: Install Dependencies on Server

```bash
# Update packages
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh
apt-get install docker-compose-plugin -y

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama in background
ollama serve &

# Pull AI models (takes 10-20 minutes)
ollama pull llama3.2:1b
ollama pull llama3.2:3b
```

---

## 📤 Step 5: Upload Your Code

On your **local Windows machine**, open a terminal and run:

```cmd
cd "C:\Users\Kushal\OneDrive\Desktop\Arpit\auralis llm"
scp -r . root@YOUR_SERVER_IP:/opt/auralis
```

---

## ⚙️ Step 6: Configure Environment on Server

```bash
cd /opt/auralis

# Create your .env file
nano .env
```

Paste this in the file (press Ctrl+S to save):
```
AURALIS_API_KEY=my_super_secret_key_2026
PORT=8000
OLLAMA_HOST=http://localhost:11434
```

---

## 📦 Step 7: Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

## 🚀 Step 8: Start Auralis (Production Mode)

```bash
# Start Auralis in background (stays running after you close SSH)
nohup python auralis_api.py > auralis.log 2>&1 &

# Check if it started:
curl http://localhost:8000/health
```

You should see: `{"status":"online","model":"llama3.2:3b",...}`

---

## 🌐 Step 9: Open the Firewall

```bash
ufw allow 8000/tcp
ufw enable
```

Your API is now live at:
```
http://YOUR_SERVER_IP:8000
```

---

## 🔑 Step 10: Share With Users

Give your users the API key from your `.env` file. They call the API like this:

```python
import requests

API_KEY = "my_super_secret_key_2026"
SERVER   = "http://YOUR_SERVER_IP:8000"

response = requests.post(
    f"{SERVER}/process",
    json={"speaker": "Alice", "transcript": "Budget approved for $50k"},
    headers={"X-API-KEY": API_KEY}
)
print(response.json())
```

---

## ✅ Step 11: Verify Everything Works

Run from your local machine:
```cmd
python test_api.py
```
Change `BASE_URL` in `test_api.py` to point to your server IP first:
```python
BASE_URL = "http://YOUR_SERVER_IP:8000"
```

---

## 🔒 Optional: Add HTTPS (Recommended for Production)

For HTTPS, install Caddy (free SSL auto-renewal):

```bash
apt install -y caddy

# Create Caddy config
nano /etc/caddy/Caddyfile
```

Add this (replace with your domain):
```
your-domain.com {
    reverse_proxy localhost:8000
}
```

```bash
systemctl reload caddy
```

Now your API is accessible at `https://your-domain.com` with free SSL! ✅

---

## 📊 Monitor Your Server

```bash
# Check Auralis logs
tail -f /opt/auralis/auralis.log

# Check server resource usage
htop
```

---

## 🛑 Stop/Restart Auralis

```bash
# Find Auralis process
ps aux | grep auralis_api

# Stop it
kill <PID>

# Restart
cd /opt/auralis && nohup python auralis_api.py > auralis.log 2>&1 &
```

---

*Auralis AI — Private, Powerful, Deployable.*
