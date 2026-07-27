import json
import logging
from groq_client import _client, GROQ_MODEL, GROQ_API_KEY

def classify_input(text: str) -> dict:
    """
    Classify user input into DREAM, AMBIGUOUS, or NON_DREAM.
    Returns a dict with:
      - classification (str): DREAM, AMBIGUOUS, or NON_DREAM
      - reasoning (str): brief explanation
      - confidence (float): 0.0 to 1.0
    """
    default_response = {
        "classification": "DREAM",
        "reasoning": "Fallback classification due to processing error.",
        "confidence": 0.5
    }

    if not text or not text.strip():
        return {
            "classification": "NON_DREAM",
            "reasoning": "Empty input provided.",
            "confidence": 1.0
        }

    # Basic local heuristics to fail fast or handle obvious non-dreams (e.g. math queries)
    stripped = text.strip().lower()
    if stripped in ["hello", "hi", "how are you", "what is 2+3", "what is 2 + 3", "2+3", "explain python", "write a poem", "what is the weather"]:
        return {
            "classification": "NON_DREAM",
            "reasoning": "Determined via local heuristics as non-dream query.",
            "confidence": 1.0
        }

    if not GROQ_API_KEY:
        # Fallback to simple local rule if API key is missing
        return default_response

    system_prompt = (
        "You are a Dream Classifier. Your sole task is to classify the user's input text into one of three categories:\n"
        "1. \"DREAM\" - The user describes a dream, nightmare, recurring dream, or dream-like personal experience.\n"
        "2. \"AMBIGUOUS\" - The user provides a short symbol or fragment that could be related to a dream but lacks narrative context (e.g. \"snake\", \"falling\", \"water\", \"dark forest\").\n"
        "3. \"NON_DREAM\" - The user asks general questions, math, programming, jokes, weather, writing tasks, or unrelated advice (e.g. \"What is 2+3?\", \"Explain Python\", \"Write a poem\", \"What is the weather?\").\n\n"
        "You must return a JSON object with exactly the following schema:\n"
        "{\n"
        "  \"classification\": \"DREAM\" | \"AMBIGUOUS\" | \"NON_DREAM\",\n"
        "  \"reasoning\": \"A brief explanation of why this classification was chosen.\",\n"
        "  \"confidence\": 0.0 to 1.0\n"
        "}\n\n"
        "Only output valid JSON. Do not wrap in markdown or add notes."
    )

    try:
        client = _client()
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Input: \"{text}\""}
            ],
            response_format={"type": "json_object"},
            temperature=0.0,
            max_tokens=150
        )
        content = (response.choices[0].message.content or "").strip()
        data = json.loads(content)
        
        # Validate schema
        classification = data.get("classification")
        if classification not in ["DREAM", "AMBIGUOUS", "NON_DREAM"]:
            data["classification"] = "DREAM"
        
        data["confidence"] = float(data.get("confidence", 0.5))
        return data
    except Exception as e:
        logging.error(f"Error in classify_input: {e}")
        # Fallback heuristic
        words = text.lower().split()
        if len(words) < 3:
            return {
                "classification": "AMBIGUOUS",
                "reasoning": "Very short input, potential symbol.",
                "confidence": 0.6
            }
        # If contains common dream triggers
        dream_triggers = ["dream", "nightmare", "slept", "woke", "chased", "flying", "saw", "was running"]
        if any(trigger in text.lower() for trigger in dream_triggers):
            return {
                "classification": "DREAM",
                "reasoning": "Contains dream-related keywords.",
                "confidence": 0.7
            }
        return default_response
