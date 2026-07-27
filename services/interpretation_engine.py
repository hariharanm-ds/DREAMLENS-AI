import json
import logging
from groq_client import _client, GROQ_MODEL, GROQ_API_KEY

def generate_interpretations(dream_text: str, extracted_data: dict) -> dict:
    """
    Generates 2 to 4 possible interpretations (hypotheses) and a turning point scenario simulation.
    Ensures language is exploratory and cautious (e.g. "may suggest", "could reflect").
    """
    default_schema = {
        "hypotheses": [
            {
                "title": "Exploratory Reflection",
                "explanation": "The dream text may suggest a general processing of waking events.",
                "evidence": "General dream content.",
                "confidence": "Moderate",
                "validation_condition": "How this relates to current transitions in waking life."
            }
        ],
        "turning_point_simulation": {
            "turning_point_description": "A specific conflict or action point in the dream.",
            "reflective_question": "What might happen if you responded differently?",
            "alternative_scenario": "A brief alternative scenario where you chose confrontation or acceptance.",
            "disclaimer": "Reflective Scenario — Not a prediction or interpretation of the future."
        }
    }

    if not GROQ_API_KEY:
        return default_schema

    system_prompt = (
        "You are an expert dream intelligence engine. Your task is to generate multiple possible interpretations and a reflective scenario simulation.\n"
        "Crucial Guidance:\n"
        "- Never say 'this dream definitely means...' or diagnose the user.\n"
        "- Use cautious, exploratory phrases: 'may suggest', 'could reflect', 'one possible reading is', 'this may be connected to'.\n"
        "- Generate between 2 and 4 distinct hypotheses.\n"
        "- Extract the major turning point or blocker and simulate a creative, alternative narrative reflecting acceptance or confrontation instead of escape.\n\n"
        "Return a JSON object conforming exactly to this schema:\n"
        "{\n"
        "  \"hypotheses\": [\n"
        "    {\n"
        "      \"title\": \"Hypothesis title (e.g., Avoidance of Waking Conflict)\",\n"
        "      \"explanation\": \"Why this interpretation fits psychologically\",\n"
        "      \"evidence\": \"Specific events or symbols from the dream that support this\",\n"
        "      \"confidence\": \"Low | Moderate | High\",\n"
        "      \"validation_condition\": \"What waking life context or memory would make this interpretation more relevant to the dreamer\"\n"
        "    }\n"
        "  ],\n"
        "  \"turning_point_simulation\": {\n"
        "    \"turning_point_description\": \"Brief description of the key conflict or blocker (e.g., facing the locked door)\",\n"
        "    \"reflective_question\": \"What if you had made a different choice? (e.g., what if the door opened?)\",\n"
        "    \"alternative_scenario\": \"A hypothetical narrative illustrating a positive, alternative resolution\",\n"
        "    \"disclaimer\": \"Reflective Scenario — Not a prediction or interpretation of the future.\"\n"
        "  }\n"
        "}\n\n"
        "Output ONLY valid JSON. No markdown wrappers."
    )

    user_prompt = f"Dream: \"{dream_text}\"\nExtracted Feature Metrics: {json.dumps(extracted_data)}"

    try:
        client = _client()
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=650
        )
        content = (response.choices[0].message.content or "").strip()
        data = json.loads(content)

        # Enforce list structure for hypotheses
        if not isinstance(data.get("hypotheses"), list) or len(data["hypotheses"]) == 0:
            data["hypotheses"] = default_schema["hypotheses"]
        
        # Enforce keys in turning point simulation
        tps = data.get("turning_point_simulation")
        if not isinstance(tps, dict):
            data["turning_point_simulation"] = default_schema["turning_point_simulation"]
        else:
            tps["disclaimer"] = "Reflective Scenario — Not a prediction or interpretation of the future."
            
        return data
    except Exception as e:
        logging.error(f"Error in generate_interpretations: {e}")
        return default_schema


def refine_interpretation(dream_text: str, original_analysis: dict, feedback_category: str, feedback_resonance: str, feedback_text: str) -> dict:
    """
    Refines the current interpretations and reports based on explicit user feedback.
    """
    default_refinement = {
        "refined_report": {},
        "refined_hypotheses": [],
        "refinement_summary": "I've refined the analysis based on your feedback."
    }

    if not GROQ_API_KEY:
        return default_refinement

    system_prompt = (
        "You are a dream intelligence guide. The user has reviewed their dream analysis and provided feedback.\n"
        "Your task is to update and refine the hypotheses and core insights to directly reflect the user's feedback.\n"
        "Acknowledge what they clarified, correct any misunderstandings, adjust confidence scales, and provide a revised reflection.\n\n"
        "Return a JSON object conforming exactly to this schema:\n"
        "{\n"
        "  \"refined_report\": {\n"
        "    \"what_mind_exploring\": \"updated summary incorporating the feedback\",\n"
        "    \"central_tension\": \"updated explanation of the conflict if affected\",\n"
        "    \"reflection_questions\": [\"three updated, even more targeted questions\"]\n"
        "  },\n"
        "  \"refined_hypotheses\": [\n"
        "    {\n"
        "      \"title\": \"Hypothesis title\",\n"
        "      \"explanation\": \"Updated explanation taking feedback into account\",\n"
        "      \"evidence\": \"Supporting elements\",\n"
        "      \"confidence\": \"Low | Moderate | High\",\n"
        "      \"validation_condition\": \"Waking life contexts\"\n"
        "    }\n"
        "  ],\n"
        "  \"refinement_summary\": \"A short, warm, supportive message summarizing how the feedback was integrated.\"\n"
        "}\n\n"
        "Output ONLY valid JSON."
    )

    user_prompt = (
        f"Dream: \"{dream_text}\"\n"
        f"Original Analysis: {json.dumps(original_analysis)}\n"
        f"Feedback Category: {feedback_category}\n"
        f"Feedback Resonance: {feedback_resonance}\n"
        f"User Note: \"{feedback_text}\""
    )

    try:
        client = _client()
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=600
        )
        content = (response.choices[0].message.content or "").strip()
        data = json.loads(content)
        return data
    except Exception as e:
        logging.error(f"Error in refine_interpretation: {e}")
        return default_refinement
