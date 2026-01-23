"""
DREAMLENS AI
LLM-Centered Generative Dream Interpretation Engine
"""

import os
import csv
import requests
from flask import Flask, request, jsonify, render_template
from pathlib import Path

app = Flask(__name__)

# =====================================================
# LOAD SYMBOL DATABASE (GROUNDING ONLY)
# =====================================================

def load_symbol_database():
    csv_path = Path(__file__).parent / "project" / "cleaned_dream_interpretations.csv"
    data = []

    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append({
                    "symbol": row.get("Word", "").strip(),
                    "meaning": row.get("Interpretation", "").strip()
                })
    except Exception as e:
        print("Symbol DB load error:", e)

    return data


SYMBOL_DATABASE = load_symbol_database()

# =====================================================
# DREAMLENS LLM ENGINE
# =====================================================

class DreamLensLLM:
    """
    LLM-first dream interpretation engine.
    """

    def __init__(self):
        self.llm_url = os.getenv("LOCAL_LLM_API_URL", "http://localhost:11434/api/generate")
        # Default to empty model so callers can omit model if the local server doesn't require it
        self.llm_model = os.getenv("LOCAL_LLM_MODEL", "")

    # -------------------------------------------------
    # BASIC EXTRACTION (ONLY FOR PROMPT CONTEXT)
    # -------------------------------------------------

    def extract_context(self, dream_text):
        text = dream_text.lower()

        actions = [
            w for w in [
                "running", "flying", "falling", "chasing", "fighting",
                "swimming", "escaping", "hiding", "climbing"
            ] if w in text
        ]

        settings = [
            w for w in [
                "house", "water", "forest", "sky", "road",
                "room", "dark", "light"
            ] if w in text
        ]

        emotions = [
            w for w in [
                "fear", "happy", "sad", "anxious", "angry",
                "peaceful", "confused"
            ] if w in text
        ]

        matched_symbols = [
            s for s in SYMBOL_DATABASE
            if s["symbol"].lower() in text
        ][:5]

        return {
            "actions": actions,
            "settings": settings,
            "emotions": emotions,
            "symbols": matched_symbols
        }

    # -------------------------------------------------
    # CORE LLM INTERPRETATION
    # -------------------------------------------------

    def interpret_dream(self, dream_text):
        context = self.extract_context(dream_text)

        prompt = f"""
You are DreamLens AI, a compassionate and insightful dream interpreter.

TASK:
Interpret the user's dream using psychological and Jungian perspectives.
Do NOT do keyword explanations.
Connect symbols, emotions, and actions into a coherent meaning.
Avoid absolute claims. Encourage reflection.

USER DREAM:
\"\"\"{dream_text}\"\"\"

DETECTED CONTEXT (for guidance, not strict rules):
Actions: {context['actions']}
Settings: {context['settings']}
Emotional cues: {context['emotions']}

Symbol references (background knowledge):
{context['symbols']}

OUTPUT STRUCTURE:
1. Overall meaning of the dream
2. Emotional and psychological insight
3. Possible real-life reflection
4. Gentle advice or reflection question

Tone: calm, supportive, human.
Length: 400–700 words.
"""

        return self.call_llm(prompt)

    # -------------------------------------------------
    # LLM CALL
    # -------------------------------------------------

    def call_llm(self, prompt, timeout=25):
        payload = {"prompt": prompt, "stream": False}
        if self.llm_model:
            payload["model"] = self.llm_model

        try:
            response = requests.post(
                self.llm_url,
                json=payload,
                timeout=timeout
            )

            if response.status_code == 200:
                # try to parse JSON safely
                try:
                    data = response.json()
                except ValueError:
                    return response.text

                # common response fields across local LLM servers
                for key in ("response", "text", "result", "output", "answer", "data"):
                    if key in data and isinstance(data[key], str):
                        return data[key]

                # some servers return choices list
                if "choices" in data and isinstance(data["choices"], list) and data["choices"]:
                    first = data["choices"][0]
                    if isinstance(first, dict):
                        for subkey in ("text", "message", "output"):
                            if subkey in first and isinstance(first[subkey], str):
                                return first[subkey]
                    if isinstance(first, str):
                        return first

                # fallback to response text
                return response.text
            else:
                # Try a few fallback payload shapes common to local LLM servers
                body = None
                try:
                    body = response.text
                except Exception:
                    body = "<unreadable response body>"

                # If the server complains about model not found, retry without model or with 'input'
                if response.status_code in (400, 404, 422):
                    # Attempt: payload with 'input' only
                    fallbacks = [
                        {"input": prompt},
                        {"prompt": prompt},
                        {"model": self.llm_model, "input": prompt}
                    ]
                    for fb in fallbacks:
                        try:
                            r2 = requests.post(self.llm_url, json=fb, timeout=5)
                            if r2.status_code == 200:
                                try:
                                    d2 = r2.json()
                                except ValueError:
                                    return r2.text
                                for key in ("response", "text", "result", "output", "answer"):
                                    if key in d2 and isinstance(d2[key], str):
                                        return d2[key]
                                if "choices" in d2 and isinstance(d2["choices"], list) and d2["choices"]:
                                    first = d2["choices"][0]
                                    if isinstance(first, dict) and "text" in first:
                                        return first["text"]
                                    if isinstance(first, str):
                                        return first
                                return r2.text
                        except Exception:
                            continue

                suggestion = (
                    "Check LOCAL_LLM_API_URL and LOCAL_LLM_MODEL environment variables. "
                    "Ensure the URL points to your local model server's generate endpoint. "
                    "Common endpoints: 'http://localhost:11434/api/generate', 'http://localhost:11434/v1/generate', "
                    "or include the model in the path like '.../api/generate/<model>'."
                )
                return f"LLM error: status={response.status_code} body={body} -- {suggestion}"

        except Exception as e:
            return f"LLM connection error: {str(e)}"


# Initialize engine
dreamlens = DreamLensLLM()

# =====================================================
# FLASK ROUTES
# =====================================================

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat")
def chat():
    return render_template("chat.html")

@app.route("/interpret", methods=["POST"])
def interpret():
    try:
        data = request.get_json(silent=True)
        if not data:
            # Try form data or raw body fallback
            if request.form and 'dream' in request.form:
                data = {'dream': request.form.get('dream')}
            else:
                raw = (request.data or b"").decode('utf-8', errors='ignore').strip()
                if raw:
                    # attempt to treat raw body as the dream text
                    data = {'dream': raw}

        if not data or 'dream' not in data:
            return jsonify({
                "success": False,
                "message": "Request must include a 'dream' field (JSON or form body)."
            }), 400

        dream = str(data.get("dream", "")).strip()
        if len(dream) < 10:
            return jsonify({
                "success": False,
                "message": "Please describe your dream in more detail."
            }), 400

        interpretation = dreamlens.interpret_dream(dream)
        return jsonify({
            "success": True,
            "interpretation": interpretation
        })

    except Exception as e:
        # Unexpected error
        return jsonify({
            "success": False,
            "message": "Server error when processing interpretation.",
            "error": str(e)
        }), 500

@app.route("/health")
def health():
    return jsonify({
        "status": "OK",
        "engine": "LLM-Centered Dream Interpretation",
        "symbols_loaded": len(SYMBOL_DATABASE),
        "model": dreamlens.llm_model
    })


if __name__ == "__main__":
    print("==============================================")
    print(" DREAMLENS AI — LLM-BASED INTERPRETATION ENGINE ")
    print("==============================================")
    app.run(debug=True, port=5000)
