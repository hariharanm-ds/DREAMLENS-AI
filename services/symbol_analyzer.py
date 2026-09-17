import json
import logging
import os
import pandas as pd
from groq_client import safe_groq_completion, GROQ_MODEL, GROQ_API_KEY

# Pre-indexed dictionary for lightning fast O(1) symbol lookup
_SYMBOL_DICT = {}
def _init_symbol_index():
    global _SYMBOL_DICT
    if _SYMBOL_DICT:
        return
    try:
        csv_path = "project/cleaned_dream_interpretations.csv"
        if not os.path.exists(csv_path):
            csv_path = "../project/cleaned_dream_interpretations.csv"
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            for _, row in df.iterrows():
                w = str(row.get("Word", "")).strip()
                interp = str(row.get("Interpretation", "")).strip()
                if w:
                    _SYMBOL_DICT[w.lower()] = (w, interp[:180])
    except Exception as e:
        logging.error(f"Error indexing symbol database: {e}")

_init_symbol_index()

def search_symbol_meanings(dream_text: str) -> str:
    """Finds matching symbols from indexed database in 0ms."""
    if not _SYMBOL_DICT or not dream_text:
        return ""
    words = set(dream_text.lower().replace(",", " ").replace(".", " ").replace(";", " ").split())
    matched = []
    for w in words:
        if len(w) > 3 and w in _SYMBOL_DICT:
            orig_word, interp = _SYMBOL_DICT[w]
            matched.append(f"- {orig_word}: {interp}")
            if len(matched) >= 3:
                break
    return "\n".join(matched)



def analyze_symbols(dream_text: str, decomposition: dict = None) -> list:
    """
    Extracts dream symbols and analyzes their relationships.
    Uses: SYMBOL + EMOTION + ACTION + CONTEXT + CONSEQUENCE.
    """
    default_schema = [
        {
            "symbol": "unspecified",
            "general_possibilities": "unknown",
            "context": "unknown",
            "associated_emotion": "unknown",
            "user_action": "none",
            "narrative_effect": "none",
            "possible_significance": "may indicate general processing"
        }
    ]

    if not GROQ_API_KEY:
        return default_schema

    db_context = search_symbol_meanings(dream_text)

    system_prompt = (
        "You are an expert symbol analyst specializing in Jungian and narrative dream therapy.\n"
        "Your task is to identify key symbols in the dream and analyze their meaning contextually.\n"
        "Do NOT use simple, isolated dictionary entries. Evaluate how symbols interact with the dreamer's actions and emotions (e.g. water is swimming is calm vs drowning is panic).\n\n"
        "Return a JSON object conforming exactly to this schema:\n"
        "{\n"
        "  \"symbols\": [\n"
        "    {\n"
        "      \"symbol\": \"name of the symbol (e.g. water, key, door, tiger)\",\n"
        "      \"general_possibilities\": \"general/cultural symbolic meanings of this symbol\",\n"
        "      \"context\": \"how this specific symbol appeared in this dream\",\n"
        "      \"associated_emotion\": \"the emotion felt or expressed around this symbol\",\n"
        "      \"user_action\": \"what the dreamer did with or in relation to this symbol\",\n"
        "      \"narrative_effect\": \"how the symbol impacted the dream narrative's flow\",\n"
        "      \"possible_significance\": \"what this contextual combination may suggest psychologically\"\n"
        "    }\n"
        "  ]\n"
        "}\n\n"
        "Output ONLY a valid JSON object. No markdown or wrappers."
    )

    user_prompt = f"Dream: \"{dream_text}\""
    if decomposition:
        user_prompt += f"\nDecomposition: {json.dumps(decomposition)}"
    if db_context:
        user_prompt += f"\n\nHere are database search matches from a dream symbol index for inspiration:\n{db_context}"

    try:
        content = safe_groq_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model=GROQ_MODEL,
            response_format={"type": "json_object"},  # Groq JSON mode requires json object root
            temperature=0.2,
            max_tokens=350
        )
        data = json.loads(content)

        # Groq response format must be an object, let's extract array if they wrapped it
        if isinstance(data, dict):
            # Look for list in dict values
            for val in data.values():
                if isinstance(val, list):
                    return val
            if "symbols" in data:
                return data["symbols"]
            # Otherwise construct a list
            return [data]
        elif isinstance(data, list):
            return data
        
        return default_schema
    except Exception as e:
        logging.error(f"Error in analyze_symbols: {e}")
        return default_schema
