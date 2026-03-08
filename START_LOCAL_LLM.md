# Career Co-Pilot - How to Start Your Local Llama3.1 Server

## ⚠️ Current Status
Your Career Co-Pilot backend is ready, but the **local LLM server is not running**.

Test results:
- ❌ Ollama (port 11434): Not running
- ❌ Custom LLM (port 8000): Not running

## Quick Start - Run This Now!

### Option 1: Using Ollama (RECOMMENDED ✅)

**Step 1: Download Ollama**
- Go to https://ollama.ai
- Download for Windows
- Install it

**Step 2: Start Ollama Server**
Open PowerShell and run:
```powershell
ollama serve
```

You should see:
```
binding 127.0.0.1:11434
listening on 127.0.0.1:11434
```

**Step 3: Pull Llama3.1 (In a NEW PowerShell window)**
```powershell
ollama pull llama3.1
```

Wait for the model to download (first time: ~5-8 GB depending on your internet)

**Step 4: Verify Connection**
```powershell
cd c:\Users\suman\jobassist\Career-Co-Pilot
python test_llm_connection.py
```

You should see:
```
✅ Ollama is running and responding!
```

---

### Option 2: Using vLLM (For Advanced Users)

**Step 1: Install vLLM**
```bash
pip install vllm
```

**Step 2: Start vLLM Server**
```bash
python -m vllm.entrypoints.openai.api_server --model meta-llama/Llama-2-7b-hf --port 8000
```

**Step 3: Configure Career Co-Pilot**
Edit `backend/.env`:
```
LOCAL_LLM_URL=http://localhost:8000
```

---

### Option 3: Using LocalAI

**Step 1: Install Docker**
- Download from https://docker.com

**Step 2: Run LocalAI**
```bash
docker run -p 8080:8080 -ti localai/localai:latest-gpu
```

**Step 3: Configure Career Co-Pilot**
Edit `backend/.env`:
```
LOCAL_LLM_URL=http://localhost:8080
```

---

## Verify Everything is Working

### Step 1: Check LLM is Running
```powershell
python test_llm_connection.py
```

Expected output:
```
✅ Ollama is running and responding!
✅ LLM is ready!
```

### Step 2: Check Backend Connection
Backend logs should show:
```
[LLMClient] Initializing with local LLM at: http://localhost:11434
[LLMClient] Using endpoint: http://localhost:11434/api/generate
[LLMClient] Detected Ollama - using model: llama3.1
[LLMClient] ✅ Successfully connected to local LLM server
```

### Step 3: Test Resume Alignment
1. Go to http://localhost:5173
2. Upload a resume
3. Enter a job description
4. Click "Run Alignment"
5. Wait 30-120 seconds for generation
6. Download the aligned resume

---

## Troubleshooting

### Issue: "Ollama serve" command not found
- Make sure Ollama is installed and added to PATH
- Restart your terminal after installing
- Or use full path: `C:\Users\YourName\AppData\Local\Programs\Ollama\ollama.exe serve`

### Issue: "ollama pull llama3.1" hangs
- Your model might be downloading in the background
- Wait patiently (can take 15-30 minutes for first download)
- Or check: `ollama list` to see download progress

### Issue: Port 11434 already in use
- Another instance of Ollama might be running
- Stop it: `Get-Process ollama | Stop-Process`
- Or change port in `backend/.env`: `LOCAL_LLM_URL=http://localhost:11435`

### Issue: "Cannot connect" after Ollama starts
- Wait 5-10 seconds for Ollama to fully initialize
- Check Ollama window is still running
- Run test script: `python test_llm_connection.py`

### Issue: Backend keeps using stub response
- Check that LLM test passes first
- Restart backend after LLM is running: `stop services and start again`
- Check backend logs for `Successfully connected` message

---

## What to Do Next (Once LLM is Running)

1. ✅ Make sure Ollama is running: `ollama serve`
2. ✅ Make sure backend is running: `c:\Users\suman\jobassist\Career-Co-Pilot\start_backend.bat`
3. ✅ Make sure frontend is running: on port 5173
4. ✅ Test connection: `python test_llm_connection.py`
5. ✅ Use the app: http://localhost:5173

---

## System Requirements

For Llama3.1 on Ollama:

| Component | Requirement |
|-----------|------------|
| **GPU** | NVIDIA/AMD/Intel GPU recommended |
| **VRAM** | 8GB minimum (16GB+ recommended) |
| **RAM** | 8GB+ |
| **Disk** | 10GB+ free (for model download) |
| **Internet** | For first-time model download |

---

## Performance Tips

1. **Use GPU acceleration** - Much faster than CPU
2. **Close other apps** - Free up RAM and VRAM
3. **Monitor VRAM** - Watch `nvidia-smi` during generation
4. **Adjust timeout** - If getting timeouts, increase in `llm_client.py`

---

## Quick Commands Reference

```powershell
# Start Ollama server
ollama serve

# Download a model (in another terminal)
ollama pull llama3.1
ollama pull llama2
ollama pull mistral

# List downloaded models
ollama list

# Remove a model
ollama rm llama3.1

# Test LLM connection
cd c:\Users\suman\jobassist\Career-Co-Pilot
python test_llm_connection.py

# Check if port 11434 is in use
netstat -ano | findstr :11434

# Start Career Co-Pilot backend
c:\Users\suman\jobassist\Career-Co-Pilot\start_backend.bat

# Start Career Co-Pilot frontend
cd c:\Users\suman\jobassist\Career-Co-Pilot\frontend
python -m http.server 5173
```

---

## Next Steps

1. **Install Ollama** from https://ollama.ai (5 minutes)
2. **Run `ollama serve`** (starts the server)
3. **Run `ollama pull llama3.1`** in another terminal (5-30 minutes first time)
4. **Run `python test_llm_connection.py`** to verify
5. **Use the app** at http://localhost:5173

That's it! Your Career Co-Pilot will then use the local Llama3.1 model for all resume alignments. 🚀

---

**Last Updated:** March 8, 2026  
**Status:** Ready to go (just need to start LLM server)
