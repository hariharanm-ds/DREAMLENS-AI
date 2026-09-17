import json
import logging
from groq_client import safe_groq_completion, GROQ_MODEL, GROQ_API_KEY

def analyze_emotions(dream_text: str, decomposition: dict = None) -> dict:
    """
    Analyzes the emotional arc and experiences of the dreamer.
    Distinguishes: WHAT HAPPENED from HOW THE DREAMER FELT.
    """
    default_schema = {
        "stages": [
            {"stage": "beginning", "emotion": "calm", "intensity": 0.5},
            {"stage": "middle", "emotion": "neutral", "intensity": 0.5},
            {"stage": "ending", "emotion": "neutral", "intensity": 0.5}
        ],
        "dominant_emotion": "neutral",
        "emotional_transition": "neutral → neutral",
        "emotional_contradictions": [],
        "unresolved_emotions": []
    }

    if not GROQ_API_KEY:
        return default_schema

    system_prompt = (
        "You are an expert emotional psychologist specializing in dream analysis.\n"
        "Your task is to analyze the emotional movement across the dream.\n"
        "Distinguish clearly between WHAT HAPPENED (events) and HOW THE DREAMER FELT about what happened (internal emotions).\n\n"
        "Return a JSON object conforming exactly to this schema:\n"
        "{\n"
        "  \"stages\": [\n"
        "    { \"stage\": \"beginning\", \"emotion\": \"emotion name\", \"intensity\": 0.0 to 1.0 },\n"
        "    { \"stage\": \"middle\", \"emotion\": \"emotion name\", \"intensity\": 0.0 to 1.0 },\n"
        "    { \"stage\": \"ending\", \"emotion\": \"emotion name\", \"intensity\": 0.0 to 1.0 }\n"
        "  ],\n"
        "  \"dominant_emotion\": \"the single overall strongest emotion\",\n"
        "  \"emotional_transition\": \"string summary of transition (e.g. calm → fear → relief)\",\n"
        "  \"emotional_contradictions\": [\"list of situations where actions and feelings did not match, e.g., laughed while falling, or felt peaceful in danger\"],\n"
        "  \"unresolved_emotions\": [\"feelings that remain lingering or unaddressed at the end of the dream\"]\n"
        "}\n\n"
        "Output ONLY valid JSON. No markdown or wrappers."
    )

    prompt = f"Dream: \"{dream_text}\""
    if decomposition:
        prompt += f"\nDecomposed Elements: {json.dumps(decomposition)}"

    try:
        content = safe_groq_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            model=GROQ_MODEL,
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=400
        )
        data = json.loads(content)

        # Schema cleanups
        if not isinstance(data.get("stages"), list):
            data["stages"] = default_schema["stages"]
        else:
            for s in data["stages"]:
                s["intensity"] = float(s.get("intensity", 0.5))
        
        data["dominant_emotion"] = str(data.get("dominant_emotion", "neutral"))
        data["emotional_transition"] = str(data.get("emotional_transition", "neutral"))
        
        for list_key in ["emotional_contradictions", "unresolved_emotions"]:
            if not isinstance(data.get(list_key), list):
                data[list_key] = []
        
        return data
    except Exception as e:
        logging.error(f"Error in analyze_emotions: {e}")
        return default_schema
