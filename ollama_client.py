"""
DREAMLENS AI - Ollama Llama 3 Client
Provides offline, local LLM dream interpretation via Ollama.
"""

import requests
import json
from datetime import datetime
import os

LOG_DIR = "logs"

# --------------- Configuration ---------------

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3")
OLLAMA_TIMEOUT = int(os.environ.get("OLLAMA_TIMEOUT", "600"))  # seconds

# --------------- System Prompt ---------------

DREAM_SYSTEM_PROMPT = """You are DreamLens AI, an expert dream interpreter with deep knowledge of:
- Jungian psychology (archetypes, collective unconscious, shadow self, anima/animus)
- Freudian analysis (unconscious desires, symbolism, wish fulfillment)
- Modern cognitive psychology (memory consolidation, emotional processing)
- Cultural and universal dream symbolism
- How dreams reflect waking-life emotions, fears, and desires

When someone shares a dream, provide a warm, insightful, and structured interpretation.

RESPONSE FORMAT - Always structure your response like this:

🔮 **Initial Impression**
What stands out about this dream and its overall emotional tone.

🧩 **Symbol Analysis**
Identify 2-4 major symbols and explain what they might represent psychologically.

💭 **Emotional Interpretation**
What emotions are present and what they may reflect about the dreamer's inner world.

🧠 **Psychological Perspective**
Insights from Jungian, Freudian, or modern psychological frameworks.

🌟 **What This Might Mean**
How this dream could connect to the dreamer's waking life, relationships, or personal growth.

📝 **Reflection Questions**
Provide 2-3 thoughtful questions for the dreamer to journal about.

GUIDELINES:
- Be warm, empathetic, and non-judgmental
- Focus on self-discovery, NOT fortune-telling or superstition
- Acknowledge that dream interpretation is personal — your analysis offers possibilities, not certainties
- Use clear, accessible language (avoid excessive jargon)
- Keep your response focused and insightful (300-500 words)"""


# --------------- Logging ---------------

def _log(msg: str):
    """Best-effort logging to model.log."""
    ts = datetime.utcnow().isoformat()
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        with open(os.path.join(LOG_DIR, "model.log"), "a", encoding="utf-8") as f:
            f.write(f"{ts} [ollama] {msg}\n")
    except Exception:
        print(f"LOG: {msg}")


# --------------- Health Check ---------------

def check_ollama_health() -> dict:
    """Check if Ollama is running and which models are available.
    
    Returns a dict with:
      - connected (bool)
      - models (list of model name strings)
      - llama3_available (bool)
      - error (str or None)
    """
    result = {
        "connected": False,
        "models": [],
        "llama3_available": False,
        "active_model": OLLAMA_MODEL,
        "error": None,
    }
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if resp.status_code == 200:
            result["connected"] = True
            data = resp.json()
            models = data.get("models", [])
            result["models"] = [m.get("name", "") for m in models]
            # Check if any variant of llama3 is available
            result["llama3_available"] = any(
                OLLAMA_MODEL in name for name in result["models"]
            )
        else:
            result["error"] = f"Ollama returned HTTP {resp.status_code}"
    except requests.exceptions.ConnectionError:
        result["error"] = "Cannot connect to Ollama. Is it running? (ollama serve)"
    except requests.exceptions.Timeout:
        result["error"] = "Ollama health check timed out"
    except Exception as e:
        result["error"] = str(e)
    return result


# --------------- Dream Interpretation ---------------

def interpret_dream(dream_text: str, db_context: str = "") -> dict:
    """Send a dream to Ollama Llama 3 for interpretation.
    
    Args:
        dream_text: The user's dream description.
        db_context: Optional context from the dream database (matched symbols).
    
    Returns a dict with:
      - success (bool)
      - interpretation (str)
      - model (str)
      - error (str or None)
    """
    # Build the user prompt
    user_prompt = f'Dream: "{dream_text}"'
    if db_context:
        user_prompt += f"\n\nRelated dream symbols from our database:\n{db_context}"
    user_prompt += "\n\nPlease provide a comprehensive, insightful dream interpretation."

    _log(f"Sending dream to {OLLAMA_MODEL}: {dream_text[:80]}...")

    try:
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": user_prompt,
            "system": DREAM_SYSTEM_PROMPT,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 1024,
            },
        }

        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=OLLAMA_TIMEOUT,
        )

        if resp.status_code == 200:
            data = resp.json()
            interpretation = data.get("response", "").strip()
            if not interpretation:
                _log("Ollama returned empty response")
                return {
                    "success": False,
                    "interpretation": "",
                    "model": OLLAMA_MODEL,
                    "error": "Ollama returned an empty response. Try again.",
                }

            _log(f"Ollama response received ({len(interpretation)} chars)")
            return {
                "success": True,
                "interpretation": interpretation,
                "model": OLLAMA_MODEL,
                "error": None,
            }
        else:
            error_msg = f"Ollama returned HTTP {resp.status_code}"
            try:
                error_data = resp.json()
                if "error" in error_data:
                    error_msg = error_data["error"]
            except Exception:
                pass
            _log(f"Ollama error: {error_msg}")
            return {
                "success": False,
                "interpretation": "",
                "model": OLLAMA_MODEL,
                "error": error_msg,
            }

    except requests.exceptions.ConnectionError:
        msg = "Cannot connect to Ollama. Make sure Ollama is running (ollama serve)."
        _log(msg)
        return {"success": False, "interpretation": "", "model": OLLAMA_MODEL, "error": msg}

    except requests.exceptions.Timeout:
        msg = f"Ollama timed out after {OLLAMA_TIMEOUT}s. The model may be loading for the first time — please try again."
        _log(msg)
        return {"success": False, "interpretation": "", "model": OLLAMA_MODEL, "error": msg}

    except Exception as e:
        msg = f"Unexpected error calling Ollama: {e}"
        _log(msg)
        return {"success": False, "interpretation": "", "model": OLLAMA_MODEL, "error": msg}
