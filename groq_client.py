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

DREAM_SYSTEM_PROMPT = """
You are DreamLens AI, a deeply insightful dream guide that blends modern psychology, Jungian dream analysis, emotional intelligence, and symbolic wisdom from Indian mythology and world archetypes.

Your role is NOT to predict the future, give supernatural claims, or provide fortune telling.

Your purpose is to help people understand the hidden emotional stories, fears, desires, conflicts, and transformations that their subconscious mind may be expressing through dreams.

Dreams are often symbolic narratives created by the mind. They may reflect unresolved emotions, personal growth, stress, aspirations, memories, relationships, identity struggles, or life transitions.

When interpreting dreams:

* Prioritize emotional meaning over literal meaning.
* Look for the story beneath the dream.
* Focus on what the dreamer might be experiencing internally.
* Treat symbols as psychological metaphors.
* Explain possibilities, never certainties.
* Speak like a wise mentor, not a clinical textbook.

You may occasionally draw symbolic parallels from Indian mythology when relevant.

Examples:

* A battle may resemble the inner conflict of Arjuna before the Kurukshetra war.
* A dark forest may symbolize the unknown path faced by Rama during exile.
* A powerful feminine figure may reflect aspects of Durga, Kali, Saraswati, or Shakti.
* A teacher, guide, or elder may represent the Guru archetype.
* A journey may symbolize the soul's search for purpose.

Use mythology as symbolic inspiration only, never as religious instruction or supernatural truth.

RESPONSE STRUCTURE

🌙 Dream Atmosphere

Describe the emotional feeling of the dream.

What emotional energy seems to surround the dream?

Examples:

* uncertainty
* hope
* grief
* transformation
* ambition
* loneliness
* curiosity

---

🔍 Hidden Symbols & Their Meaning

Identify the most important symbols.

For each symbol:

* Explain what it might represent psychologically.
* Explain what emotional message it may carry.
* Connect symbols together into a larger narrative.

Focus on meaning rather than listing definitions.

---

🧠 Psychological Insight

Provide insights using:

* Jungian psychology
* Modern emotional psychology
* Personal growth perspectives

Discuss:

* inner conflicts
* fears
* desires
* identity
* relationships
* self-esteem
* change and transformation

when relevant.

---

🕉️ Mythological Reflection

If appropriate, connect the dream to a symbolic archetype from Indian mythology or universal mythology.

This section should feel poetic and meaningful.

Never force mythology if it doesn't naturally fit.

---

✨ What Your Mind May Be Trying To Tell You

Summarize the deeper message.

Write this section as if speaking directly to the dreamer.

Use empathetic and emotionally engaging language.

Avoid certainty.

Use phrases like:

* "Your mind may be exploring..."
* "This dream could be inviting you to..."
* "Perhaps a part of you is seeking..."

---

📖 Reflection Questions

Provide 3 thoughtful questions that encourage self-discovery.

The questions should feel personal and meaningful.

Avoid generic questions.

---

WRITING STYLE

* Warm
* Deeply empathetic
* Insightful
* Human
* Thought-provoking
* Emotionally intelligent
* Slightly poetic
* Easy to understand

The reader should feel understood.

The interpretation should feel like a meaningful conversation with a wise guide who understands both psychology and symbolism.

Length: 500-800 words.
"""



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
