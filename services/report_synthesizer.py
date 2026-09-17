import json
import logging
from groq_client import safe_groq_completion, GROQ_MODEL, GROQ_API_KEY

def synthesize_report(dream_text: str, extracted_data: dict, interpretations: dict) -> dict:
    """
    Synthesizes the final structured report from intermediate analysis outputs.
    Ensures language is exploratory, compassionate, and psychologically thoughtful.
    """
    default_schema = {
        "atmosphere": "A quiet processing of everyday thoughts and events.",
        "story_map": "Beginning → Middle → Ending",
        "emotional_arc_text": "Neutral emotional movement.",
        "symbol_relationships_text": "Symbols were parsed individually but show general waking-life significance.",
        "central_tension": "No major contradictions detected.",
        "psychological_lenses": {
            "emotional_psychology": "Emotions are in a steady state, processing daily adjustments.",
            "jungian_lens": "Indicates standard conscious-unconscious balancing.",
            "narrative_psychology": "The dreamer acts as a general observer.",
            "personal_growth": "Points to continuous adaptation."
        },
        "mythological_reflection": "",
        "what_mind_exploring": "Your mind may be processing general thoughts about control and navigation.",
        "reflection_questions": [
            "What did this dream remind you of in waking life?",
            "How did you feel when you woke up?",
            "What would you change about the dream ending?"
        ],
        "uncertainty_note": "Dream exploration is highly subjective. This report is a reflective tool to assist your self-discovery, not a fact or medical advice."
    }

    if not GROQ_API_KEY:
        return default_schema

    system_prompt = (
        "You are an expert dream report synthesizer.\n"
        "Your task is to take a dream and its structured analysis metrics, and generate a synthesized Dream Intelligence Report in JSON format.\n"
        "Crucial Guidelines:\n"
        "- Adopt a warm, wise, empathetic, and reflective tone.\n"
        "- Never diagnose, predict, or offer clinical labels. Keep interpretations subjective, exploratory, and open-ended.\n"
        "- Use cautious language: 'may suggest', 'could reflect', 'one possible interpretation is', 'this may be connected to'.\n"
        "- For the Mythological Reflection, only connect to archetypes (e.g. Arjuna's conflict, Rama's journey, Durga's resolve, etc.) if it naturally fits. Otherwise, leave it as an empty string. Never force it.\n\n"
        "Return a JSON object conforming exactly to this schema:\n"
        "{\n"
        "  \"atmosphere\": \"Description of the emotional energy and tone of the dream\",\n"
        "  \"story_map\": \"Progression timeline: Beginning → Trigger → Conflict → Turning Point → Ending\",\n"
        "  \"emotional_arc_text\": \"Explanation of the emotional transitions, distinguishing events from the dreamer's internal feelings\",\n"
        "  \"symbol_relationships_text\": \"How the symbols interact contextually in a larger narrative, rather than isolated definitions\",\n"
        "  \"central_tension\": \"The core psychological contradiction or tension detected in the dream narrative\",\n"
        "  \"psychological_lenses\": {\n"
        "    \"emotional_psychology\": \"Insights from emotional psychology regarding stress, regulation, avoidance, or desire\",\n"
        "    \"jungian_lens\": \"Insights regarding Shadow, Persona, archetypes, and unconscious struggles\",\n"
        "    \"narrative_psychology\": \"Insights on agency, self-perception, and the protagonist role\",\n"
        "    \"personal_growth\": \"Insights on life transitions, decisions, and confronting challenges\"\n"
        "  },\n"
        "  \"mythological_reflection\": \"An optional poetic comparison to an Indian or universal mythological archetype (or empty string if not applicable)\",\n"
        "  \"what_mind_exploring\": \"Empathetic summary of what the subconscious may be exploring, addressed directly to the dreamer\",\n"
        "  \"reflection_questions\": [\"three highly customized, personalized reflection questions based on this dream's specific symbols and conflicts\"],\n"
        "  \"uncertainty_note\": \"Reflective reminder that interpretations are subjective, exploratory, and lack clinical certainty\"\n"
        "}\n\n"
        "Output ONLY valid JSON. No markdown wrappers."
    )

    user_prompt = (
        f"Dream: \"{dream_text}\"\n"
        f"Extracted Features: {json.dumps(extracted_data)}\n"
        f"Interpretations & Hypotheses: {json.dumps(interpretations)}"
    )

    try:
        content = safe_groq_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model=GROQ_MODEL,
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=600
        )
        data = json.loads(content)

        # Structure checks
        if not isinstance(data.get("psychological_lenses"), dict):
            data["psychological_lenses"] = default_schema["psychological_lenses"]
        if not isinstance(data.get("reflection_questions"), list) or len(data["reflection_questions"]) == 0:
            data["reflection_questions"] = default_schema["reflection_questions"]
            
        data["uncertainty_note"] = "Dream exploration is highly subjective. This report is a reflective tool to assist your self-discovery, not a fact or medical advice."
        return data
    except Exception as e:
        logging.error(f"Error in synthesize_report: {e}")
        return default_schema
