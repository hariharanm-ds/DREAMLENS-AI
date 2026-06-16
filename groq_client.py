"""
DREAMLENS AI - Groq Client
Provides hosted LLM dream interpretation via the official Groq Python SDK.
"""

from datetime import datetime
import os
import tempfile

from groq import Groq

IS_VERCEL = bool(os.environ.get("VERCEL"))
TMP_DIR = tempfile.gettempdir()
LOG_DIR = os.environ.get("LOG_DIR", os.path.join(TMP_DIR, "dreamlens-logs") if IS_VERCEL else "logs")

# --------------- Configuration ---------------


def _load_local_env(path: str = ".env"):
    """Load simple KEY=VALUE pairs for local development without extra dependencies."""
    if not os.path.exists(path):
        return
    try:
        with open(path, "r", encoding="utf-8") as env_file:
            for raw_line in env_file:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip().lstrip("\ufeff")
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value
    except Exception:
        pass


_load_local_env()

GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GROQ_TIMEOUT = int(os.environ.get("GROQ_TIMEOUT", "120"))

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
            f.write(f"{ts} [groq] {msg}\n")
    except Exception:
        print(f"LOG: {msg}")


def _client() -> Groq:
    return Groq(api_key=GROQ_API_KEY, timeout=GROQ_TIMEOUT)


# --------------- Health Check ---------------

def check_groq_health() -> dict:
    """Check whether Groq is configured and reachable."""
    result = {
        "connected": False,
        "models": [],
        "model_available": False,
        "active_model": GROQ_MODEL,
        "provider": "groq",
        "error": None,
    }

    if not GROQ_API_KEY:
        result["error"] = "GROQ_API_KEY is not configured."
        return result

    try:
        models_response = _client().models.list()
        model_ids = [
            getattr(model, "id", "")
            for model in getattr(models_response, "data", [])
            if getattr(model, "id", "")
        ]
        result["connected"] = True
        result["models"] = model_ids
        result["model_available"] = GROQ_MODEL in model_ids if model_ids else True
        if model_ids and not result["model_available"]:
            result["error"] = f"Configured Groq model '{GROQ_MODEL}' was not found."
    except Exception as e:
        result["error"] = f"Groq health check failed: {e}"

    return result


# --------------- Dream Interpretation ---------------

def interpret_dream(dream_text: str, db_context: str = "") -> dict:
    """Send a dream to Groq for interpretation.

    Args:
        dream_text: The user's dream description.
        db_context: Optional context from the dream database (matched symbols).

    Returns a dict with:
      - success (bool)
      - interpretation (str)
      - model (str)
      - error (str or None)
    """
    user_prompt = f'Dream: "{dream_text}"'
    if db_context:
        user_prompt += f"\n\nRelated dream symbols from our database:\n{db_context}"
    user_prompt += "\n\nPlease provide a comprehensive, insightful dream interpretation."

    _log(f"Sending dream to {GROQ_MODEL}: {dream_text[:80]}...")

    if not GROQ_API_KEY:
        msg = "GROQ_API_KEY is not configured."
        _log(msg)
        return {"success": False, "interpretation": "", "model": GROQ_MODEL, "error": msg}

    try:
        response = _client().chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": DREAM_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            top_p=0.9,
            max_tokens=1024,
        )

        interpretation = ""
        if response.choices:
            interpretation = (response.choices[0].message.content or "").strip()

        if not interpretation:
            _log("Groq returned empty response")
            return {
                "success": False,
                "interpretation": "",
                "model": GROQ_MODEL,
                "error": "Groq returned an empty response. Try again.",
            }

        _log(f"Groq response received ({len(interpretation)} chars)")
        return {
            "success": True,
            "interpretation": interpretation,
            "model": GROQ_MODEL,
            "error": None,
        }

    except Exception as e:
        msg = f"Unexpected error calling Groq: {e}"
        _log(msg)
        return {"success": False, "interpretation": "", "model": GROQ_MODEL, "error": msg}
