# Career Co-Pilot Local LLM Setup Guide

## Overview

Career Co-Pilot now uses **Llama3.1** running locally on your dedicated GPU for resume alignment and generation. This eliminates dependency on external APIs and gives you full control over the LLM.

## Prerequisites

- Local LLM server (Llama3.1 or compatible) running on port 8000
- GPU with proper drivers configured
- FastAPI backend updated to use local LLM

## Quick Start

### 1. Ensure Your Local LLM is Running

Your Llama3.1 model should be running on `http://localhost:8000` with a `/generate` endpoint.

**Example setups:**

#### Using Ollama (Recommended)
```bash
# Install Ollama from https://ollama.ai
ollama pull llama3.1
ollama run llama3.1
# This will start on port 11434 by default, forward to 8000 if needed
```

#### Using vLLM
```bash
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-2-7b-hf \
    --port 8000
```

#### Using LocalAI
```bash
git clone https://github.com/go-skynet/LocalAI
cd LocalAI
docker-compose up
```

#### Using HuggingFace Transformers
```python
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
model_id = "meta-llama/Llama-2-7b-hf"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float16)
model.to("cuda")

class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: int = 256
    temperature: float = 0.7
    top_p: float = 0.95
    top_k: int = 40

@app.post("/generate")
async def generate(req: GenerateRequest):
    inputs = tokenizer(req.prompt, return_tensors="pt").to("cuda")
    outputs = model.generate(**inputs, max_new_tokens=req.max_tokens, temperature=req.temperature)
    text = tokenizer.decode(outputs[0])
    return {"generated_text": text}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 2. Configure the Backend

The backend expects to find the LLM at `http://localhost:8000/generate`.

**Optional: Override LLM URL**

Edit `backend/.env`:
```
LOCAL_LLM_URL=http://your-custom-host:port
```

### 3. Start Career Co-Pilot

```bash
cd backend
python -m uvicorn app.main:app --reload
```

Frontend: http://localhost:5173
API: http://127.0.0.1:8000

## How It Works

### Resume Alignment Workflow

1. **Resume Upload** → Extract text from .docx
2. **Job Analysis** → Parse job description from LinkedIn
3. **LLM Processing** → Send both to local Llama3.1
4. **Resume Generation** → Generate aligned resume in .docx format
5. **Download** → User downloads the aligned resume

### LLM Integration Points

**File:** `backend/app/services/llm_client.py`

- Initializes connection to local LLM on startup
- Tests the connection with a simple prompt
- Sends resume alignment prompts to `/generate` endpoint
- Handles timeout and connection errors gracefully
- Falls back to stub response if LLM is unavailable

### API Contract with Local LLM

**Request (POST /generate):**
```json
{
    "prompt": "Your prompt here",
    "max_tokens": 2000,
    "temperature": 0.4,
    "top_p": 0.95,
    "top_k": 40
}
```

**Expected Response:**
```json
{
    "generated_text": "The generated response...",
    "tokens_generated": 150,
    "inference_time_ms": 3000
}
```

## Performance Considerations

### Token Limits
- Default: 2000 tokens for alignment
- Adjust in `llm_client.py` if needed

### Temperature
- Default: 0.4 (less random, more focused)
- Range: 0.0-2.0
- Lower = more deterministic, Higher = more creative

### Timeout
- Default: 300 seconds (5 minutes)
- Adjust in `llm_client.py` for longer generations

## Troubleshooting

### Issue: "Cannot connect to local LLM at http://localhost:8000"

**Solution:**
1. Verify your LLM server is running: `curl http://localhost:8000/generate -X POST -d '{"prompt":"test"}'`
2. Check firewall settings
3. Verify port 8000 is not in use: `netstat -ano | findstr :8000`

### Issue: "Request timed out"

**Solution:**
1. Your LLM might be slow - increase timeout in `llm_client.py`
2. Check GPU usage: `nvidia-smi` (if NVIDIA GPU)
3. Reduce max_tokens for faster generation
4. Check system memory availability

### Issue: Generated resume is incomplete

**Possible causes:**
- Token limit reached → increase max_tokens
- LLM crashed → check LLM server logs
- Network timeout → increase timeout value

### Issue: Low quality resume alignment

**Solutions:**
1. Improve the alignment prompt in `alignment_service.py`
2. Use a larger model (13B instead of 7B)
3. Tune temperature (try 0.5 or 0.6)
4. Provide better base resume content

## File Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI app with .env loading
│   ├── services/
│   │   ├── llm_client.py      # Local LLM client
│   │   ├── alignment_service.py # Resume alignment logic
│   │   └── docx_service.py    # .docx generation
│   └── routers/
│       ├── alignment_router.py # Alignment endpoints
│       └── ...
├── .env                        # LOCAL_LLM_URL config
└── requirements.txt           # Python dependencies
```

## Monitoring & Debugging

### Enable Detailed Logging

Add this to `backend/app/main.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check LLM Connection

```bash
# Test the local LLM endpoint
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Generate a professional summary",
    "max_tokens": 100,
    "temperature": 0.7
  }'
```

### Monitor GPU Usage

```bash
# For NVIDIA GPU
nvidia-smi --query-gpu=memory.used,memory.free --format=csv -l 1

# For AMD GPU
rocm-smi --showmeminfo HIP
```

## Best Practices

1. **Keep LLM server separate** - Run on different GPU/process from app
2. **Use model quantization** - 8-bit or 4-bit to reduce VRAM
3. **Cache prompts** - Store templates to avoid rebuilding
4. **Monitor inference time** - Log and alert on slow responses
5. **Regular backups** - Save generated resumes
6. **Load testing** - Test with multiple concurrent requests

## Future Enhancements

- [ ] Multiple model support (GPT, Claude, etc.)
- [ ] Model switching via UI
- [ ] Inference result caching
- [ ] Batch processing for multiple resumes
- [ ] Custom prompt templates
- [ ] A/B testing different models
- [ ] Performance analytics dashboard

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review backend logs: `backend/.logs/app.log`
3. Test LLM directly with curl
4. Verify .env configuration
