import json
import logging
from groq_client import _client, GROQ_MODEL, GROQ_API_KEY

def analyze_narrative(dream_text: str, decomposition: dict = None) -> dict:
    """
    Analyzes the dream as a narrative arc and identifies the protagonist's roles/behaviors.
    """
    default_schema = {
        "starting_state": "",
        "trigger": "",
        "response": "",
        "obstacle": "",
        "decision": "",
        "consequence": "",
        "ending": "",
        "protagonist_position": "",
        "desire_or_goal": "",
        "threat": "",
        "transformation": "",
        "unresolved_conflict": "",
        "protagonist_role": "observing"
    }

    if not GROQ_API_KEY:
        return default_schema

    system_prompt = (
        "You are an expert narrative analyst specializing in psychological storytelling and dream analysis.\n"
        "Your task is to analyze the narrative arc of the dream.\n"
        "Pay special attention to the dreamer's active role (e.g., running, hiding, searching, confronting, observing, helping, escaping, returning, refusing, surrendering, etc.) and what role they play in the narrative.\n\n"
        "Return a JSON object conforming exactly to this schema:\n"
        "{\n"
        "  \"starting_state\": \"how the narrative begins\",\n"
        "  \"trigger\": \"the incident that sets off the chain of events\",\n"
        "  \"response\": \"how the dreamer reacts to the trigger\",\n"
        "  \"obstacle\": \"the challenge or barrier encountered\",\n"
        "  \"decision\": \"the choice made by the protagonist during the key event\",\n"
        "  \"consequence\": \"the outcome of that decision\",\n"
        "  \"ending\": \"the final state of the dream story\",\n"
        "  \"protagonist_position\": \"how active, passive, powerful, or helpless the dreamer is\",\n"
        "  \"desire_or_goal\": \"what the dreamer is seeking or trying to achieve\",\n"
        "  \"threat\": \"the primary force working against the dreamer\",\n"
        "  \"transformation\": \"any shift in perception, agency, or environment\",\n"
        "  \"unresolved_conflict\": \"any conflicts left hanging at the end\",\n"
        "  \"protagonist_role\": \"select one or more: running, hiding, searching, confronting, observing, helping, escaping, returning, refusing, surrendering, other\"\n"
        "}\n\n"
        "Output ONLY valid JSON. No markdown or wrappers."
    )

    user_prompt = f"Dream: \"{dream_text}\""
    if decomposition:
        user_prompt += f"\nDecomposed Elements: {json.dumps(decomposition)}"

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
            max_tokens=450
        )
        content = (response.choices[0].message.content or "").strip()
        data = json.loads(content)

        # Basic validations
        for str_key in default_schema.keys():
            if not isinstance(data.get(str_key), str):
                data[str_key] = ""
        
        return data
    except Exception as e:
        logging.error(f"Error in analyze_narrative: {e}")
        return default_schema
