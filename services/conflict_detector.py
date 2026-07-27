import json
import logging
from groq_client import _client, GROQ_MODEL, GROQ_API_KEY

def detect_conflicts(dream_text: str, decomposition: dict = None, emotions: dict = None) -> dict:
    """
    Detects psychological conflicts, tensions, and paradoxes in the dream.
    Maps them into a 2D Conflict Matrix.
    """
    default_schema = {
        "conflicts": [
            {
                "tension_type": "fear vs approach",
                "explanation": "No tensions detected.",
                "dream_evidence": "none"
            }
        ],
        "conflict_matrix": {
            "quadrant": "AVOIDANCE",
            "dimensions": {
                "fear": "moving away",
                "curiosity": "moving away",
                "control": "moving away"
            },
            "rationale": "Default matrix placement."
        }
    }

    if not GROQ_API_KEY:
        return default_schema

    system_prompt = (
        "You are an expert psychological conflict detector specializing in dream therapy.\n"
        "Your task is to identify key psychological conflicts, paradoxes, and tensions in the dream (e.g. FEAR + APPROACH, ESCAPE + CURIOSITY, WANTING TO LEAVE + BEING UNABLE TO LEAVE).\n"
        "Map the dreamer's actions and emotions into an exploratory Conflict Matrix relative to FEAR, CURIOSITY, and CONTROL along two axes: MOVING TOWARD (approaching, exploring, confronting) and MOVING AWAY (avoiding, escaping, suppressing).\n\n"
        "Return a JSON object conforming exactly to this schema:\n"
        "{\n"
        "  \"conflicts\": [\n"
        "    {\n"
        "      \"tension_type\": \"e.g. fear vs approach, escape vs curiosity, love vs rejection\",\n"
        "      \"explanation\": \"explanation of this psychological tension in the dream\",\n"
        "      \"dream_evidence\": \"specific evidence or action from the dream text\"\n"
        "    }\n"
        "  ],\n"
        "  \"conflict_matrix\": {\n"
        "    \"quadrant\": \"e.g. APPROACHING FEAR, AVOIDANCE, EXPLORATION, SUPPRESSION, CONFRONTATION, ESCAPE\",\n"
        "    \"dimensions\": {\n"
        "      \"fear\": \"moving toward or moving away\",\n"
        "      \"curiosity\": \"moving toward or moving away\",\n"
        "      \"control\": \"moving toward or moving away\"\n"
        "    },\n"
        "    \"rationale\": \"explanation of why the dream belongs in this area of the matrix\"\n"
        "  }\n"
        "}\n\n"
        "Output ONLY valid JSON. No markdown or wrappers."
    )

    user_prompt = f"Dream: \"{dream_text}\""
    if decomposition:
        user_prompt += f"\nDecomposition: {json.dumps(decomposition)}"
    if emotions:
        user_prompt += f"\nEmotions: {json.dumps(emotions)}"

    try:
        client = _client()
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=400
        )
        content = (response.choices[0].message.content or "").strip()
        data = json.loads(content)

        # Basic validations
        if not isinstance(data.get("conflicts"), list):
            data["conflicts"] = default_schema["conflicts"]
        if not isinstance(data.get("conflict_matrix"), dict):
            data["conflict_matrix"] = default_schema["conflict_matrix"]
        
        return data
    except Exception as e:
        logging.error(f"Error in detect_conflicts: {e}")
        return default_schema
