# DREAMLENS AI - OPEN SOURCE LLM SETUP

## What This Is

A **real AI dream interpreter** using **Ollama** - a free, open-source way to run powerful AI models locally on your computer.

No API keys needed. No internet required. Just pure local AI.

---

## Setup Instructions

### Step 1: Install Ollama (Free)

**Windows:**
1. Go to https://ollama.ai
2. Click "Download for Windows"
3. Run the installer
4. Complete installation

**Mac/Linux:**
```bash
curl https://ollama.ai/install.sh | sh
```

### Step 2: Download a Model

Open PowerShell and run:

```powershell
ollama pull mistral
```

This downloads Mistral (7B) - fast, smart, open-source AI model.

**Wait for it to complete (~4GB download)**

### Step 3: Start Ollama Server

Open PowerShell and run:

```powershell
ollama serve
```

**Leave this terminal open!** This runs the Ollama API server.

### Step 4: Start DreamLens AI

Open **another PowerShell window** and run:

```powershell
cd "E:\DreamLensAI\DREAMLENS AI"
python app_llm.py
```

### Step 5: Open in Browser

```
http://localhost:5000/chat
```

---

## How It Works

```
Your Dream
    |
    v
DreamLens App (Flask)
    |
    v
Ollama API
    |
    v
Mistral AI Model (Running Locally)
    |
    v
Dream Interpretation
    |
    v
Your Browser
```

**Everything runs on your computer. No data sent anywhere.**

---

## First Time Using

### In Terminal 1 (Keep Open):
```powershell
ollama serve
```

You should see:
```
Listening on 127.0.0.1:11434
```

### In Terminal 2:
```powershell
cd "E:\DreamLensAI\DREAMLENS AI"
python app_llm.py
```

You should see:
```
* Running on http://127.0.0.1:5000
```

### In Browser:
```
http://localhost:5000/chat
```

Type your dream and get AI interpretation!

---

## What Models You Can Use

**Mistral (Recommended - Fast)**
```powershell
ollama pull mistral
```
- Fast (good for responses)
- Smart (good understanding)
- ~7B parameters
- ~4GB

**Llama 2 (More Capable)**
```powershell
ollama pull llama2
```
- Slightly slower
- Better understanding
- ~7B parameters
- ~4GB

**Neural Chat (Optimized for Chat)**
```powershell
ollama pull neural-chat
```
- Good for conversations
- Fast responses
- ~7B parameters
- ~4GB

To use a different model, change `model="mistral"` to `model="llama2"` in app_llm.py

---

## Troubleshooting

### "Cannot connect to Ollama"
1. Check if Ollama is running in another terminal
2. Run: `ollama serve`
3. Refresh browser

### "Model not found"
1. Check if you downloaded the model
2. Run: `ollama pull mistral`
3. Wait for download to complete

### "Slow responses"
1. First response takes longer to load model
2. Subsequent responses are faster
3. This is normal for local LLM

### "Out of memory"
1. Ollama might need more RAM
2. Try smaller model: `ollama pull orca-mini`
3. Or increase Windows virtual memory

---

## Key Advantages

✅ **Free** - No API costs
✅ **Open Source** - Know exactly what you're running
✅ **Local** - No data sent anywhere
✅ **Private** - Your dreams stay on your computer
✅ **Real AI** - Uses actual language models
✅ **Flexible** - Switch models anytime
✅ **Offline** - Works without internet
✅ **Always Available** - No API rate limits

---

## File Structure

```
app_llm.py              - Flask app with Ollama integration
templates/chat.html     - Web interface
static/script.js        - JavaScript
project/*.csv           - Dream database (2,080 entries)
```

---

## How Dream Interpretation Works

1. You type your dream
2. DreamLens sends it to Ollama
3. Mistral AI analyzes it with:
   - Symbol analysis
   - Emotion interpretation
   - Psychological frameworks
   - Real-life connections
   - Reflection questions
4. AI generates response
5. You read full interpretation

---

## System Requirements

- **OS:** Windows 10/11, Mac, or Linux
- **RAM:** 8GB minimum (16GB recommended)
- **Disk:** 10GB free (for model)
- **Internet:** Only needed for initial download

---

## Example Dream Interpretation

### Input
```
"I was flying over the ocean, felt free and happy,
but then I was falling and couldn't control it"
```

### Output (From Real AI)
```
YOUR DREAM ANALYSIS

[Mistral AI generates comprehensive interpretation]

SYMBOL ANALYSIS
Flying represents freedom and transcendence...
Ocean symbolizes emotions and the vastness of possibilities...
Falling indicates loss of control and fear...

EMOTIONAL INTERPRETATION
The contrast between freedom and fear shows internal conflict...
You may be experiencing something wonderful but also uncertain...

PSYCHOLOGICAL PERSPECTIVE
From a Jungian view, this represents the tension between...
Freudian interpretation suggests...
Modern psychology sees this as processing change...

WHAT THIS MIGHT MEAN FOR YOU
Consider areas in your life where you're experiencing both joy and anxiety...
This dream may reflect a major transition...

REFLECTION QUESTIONS
1. What in your waking life feels both exciting and scary?
2. Is there something you want but are afraid to pursue?
3. How can you find safety while taking risks?
4. What would it mean to "land safely"?
```

**Real AI generates this - not templates!**

---

## Getting Started Now

### Quick Start (5 minutes)

1. **Install Ollama:**
   - Download from https://ollama.ai
   - Run installer
   
2. **Download Model:**
   ```powershell
   ollama pull mistral
   ```
   (Wait ~5 minutes)

3. **Start Ollama:**
   ```powershell
   ollama serve
   ```
   (Keep terminal open)

4. **Start DreamLens:**
   ```powershell
   cd "E:\DreamLensAI\DREAMLENS AI"
   python app_llm.py
   ```

5. **Open Browser:**
   ```
   http://localhost:5000/chat
   ```

6. **Type Your Dream & Get AI Interpretation!**

---

## Next Steps

- Try different dreams
- Test different models
- Customize model settings
- Explore Ollama options

---

**You now have a REAL open-source AI dream interpreter!**

**Start with: http://localhost:5000/chat**

---

Version: 1.0 (Open Source LLM Edition)
Date: December 21, 2025
Status: Ready for Setup
