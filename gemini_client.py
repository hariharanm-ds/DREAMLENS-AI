"""
DREAMLENS AI - Google Gemini Client
Provides cloud-based LLM dream interpretation via the Gemini API.
"""

import os
from datetime import datetime
from google import genai
from google.genai import types

LOG_DIR = "/tmp/logs" if os.environ.get("VERCEL") else "logs"

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

def _log(msg: str):
    """Best-effort logging to model.log."""
    ts = datetime.utcnow().isoformat()
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        with open(os.path.join(LOG_DIR, "model.log"), "a", encoding="utf-8") as f:
            f.write(f"{ts} [gemini] {msg}\n")
    except Exception:
        print(f"LOG: {msg}")

def interpret_dream(dream_text: str, db_context: str = "") -> dict:
    """Send a dream to Gemini for interpretation."""
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {"success": False, "interpretation": "", "model": "gemini", "error": "GEMINI_API_KEY not found"}

    try:
        client = genai.Client(api_key=api_key)
        
        user_prompt = f'Dream: "{dream_text}"'
        if db_context:
            user_prompt += f"\n\nRelated dream symbols from our database:\n{db_context}"
        user_prompt += "\n\nPlease provide a comprehensive, insightful dream interpretation."

        _log(f"Sending dream to Gemini: {dream_text[:80]}...")

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=DREAM_SYSTEM_PROMPT,
                temperature=0.7,
                top_p=0.9,
            ),
        )

        interpretation = response.text.strip()
        
        if not interpretation:
            _log("Gemini returned empty response")
            return {
                "success": False,
                "interpretation": "",
                "model": "gemini-2.5-flash",
                "error": "Gemini returned an empty response. Try again.",
            }

        _log(f"Gemini response received ({len(interpretation)} chars)")
        return {
            "success": True,
            "interpretation": interpretation,
            "model": "gemini-2.5-flash",
            "error": None,
        }

    except Exception as e:
        msg = f"Unexpected error calling Gemini: {e}"
        _log(msg)
        return {"success": False, "interpretation": "", "model": "gemini-2.5-flash", "error": msg}
