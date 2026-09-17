import json
import logging
from groq_client import safe_groq_completion, GROQ_MODEL, GROQ_API_KEY

def decompose_dream(dream_text: str) -> dict:
    """
    Decomposes dream text into setting, characters, objects, events, actions,
    transitions, beginning_state, triggering_event, central_conflict, climax,
    ending, and unresolved_elements.
    """
    default_schema = {
        "setting": [],
        "characters": [],
        "objects": [],
        "events": [],
        "actions": [],
        "transitions": [],
        "beginning_state": "",
        "triggering_event": "",
        "central_conflict": "",
        "climax": "",
        "ending": "",
        "unresolved_elements": []
    }

    if not GROQ_API_KEY:
        return default_schema

    system_prompt = (
        "You are an expert dream narrative parser. Your task is to identify and decompose the structural elements of the dream.\n"
        "Do not invent any details. Extract only what is explicitly described or directly implied in the text. Use null or empty lists for missing elements.\n\n"
        "Return a JSON object conforming exactly to this schema:\n"
        "{\n"
        "  \"setting\": [\"locations or environments\"],\n"
        "  \"characters\": [\"people, animals, unknown figures, creatures\"],\n"
        "  \"objects\": [\"objects, colors, weather, symbols\"],\n"
        "  \"events\": [\"key events or occurrences\"],\n"
        "  \"actions\": [\"physical or verbal actions\"],\n"
        "  \"transitions\": [\"shifts in scene, time, or state\"],\n"
        "  \"beginning_state\": \"how the dream narrative starts\",\n"
        "  \"triggering_event\": \"what prompts the central action\",\n"
        "  \"central_conflict\": \"the core conflict or barrier\",\n"
        "  \"climax\": \"the peak intensity or turning point\",\n"
        "  \"ending\": \"how the dream finishes\",\n"
        "  \"unresolved_elements\": [\"elements left hanging or open\"]\n"
        "}\n\n"
        "Output ONLY valid JSON. No markdown or wrappers."
    )

    try:
        content = safe_groq_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Dream: \"{dream_text}\""}
            ],
            model=GROQ_MODEL,
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=500
        )
        data = json.loads(content)

        # Enforce defaults and clean types
        for list_key in ["setting", "characters", "objects", "events", "actions", "transitions", "unresolved_elements"]:
            if not isinstance(data.get(list_key), list):
                data[list_key] = []
        for str_key in ["beginning_state", "triggering_event", "central_conflict", "climax", "ending"]:
            if not isinstance(data.get(str_key), str):
                data[str_key] = ""

        return data
    except Exception as e:
        logging.error(f"Error in decompose_dream: {e}")
        return default_schema
