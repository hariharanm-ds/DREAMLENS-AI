import json
import logging
import os
import pandas as pd
from groq_client import _client, GROQ_MODEL, GROQ_API_KEY

# Load database locally for self-contained execution
def load_symbol_database():
    try:
        csv_path = "project/cleaned_dream_interpretations.csv"
        if not os.path.exists(csv_path):
            # Try parent path fallback
            csv_path = "../project/cleaned_dream_interpretations.csv"
        
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            if "Word" in df.columns and "Interpretation" in df.columns:
                return df
        return pd.DataFrame(columns=["Word", "Interpretation"])
    except Exception as e:
        logging.error(f"Error loading symbol database in symbol_analyzer: {e}")
        return pd.DataFrame(columns=["Word", "Interpretation"])

dreams_df = load_symbol_database()

def search_symbol_meanings(dream_text: str) -> str:
    """Finds matching symbols from database to supply context to the LLM."""
    if dreams_df.empty:
        return ""
    dream_words = dream_text.lower().split()
    results = []
    for _, row in dreams_df.iterrows():
        word = str(row["Word"]).lower()
        # Find matches where words align
        matches = sum(1 for w in dream_words if w == word or (len(w) > 3 and w in word) or (len(word) > 3 and word in w))
        if matches > 0:
            results.append({
                "word": row["Word"],
                "interpretation": str(row["Interpretation"])[:200],
                "relevance": matches
            })
    
    results.sort(key=lambda x: x["relevance"], reverse=True)
    if not results:
        return ""
    
    context_parts = []
    for r in results[:4]:
        context_parts.append(f"- {r['word']}: {r['interpretation']}...")
    return "\n".join(context_parts)


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
        "Return a JSON array of symbol dictionaries conforming exactly to this schema:\n"
        "[\n"
        "  {\n"
        "    \"symbol\": \"name of the symbol (e.g. water, key, door, tiger)\",\n"
        "    \"general_possibilities\": \"general/cultural symbolic meanings of this symbol\",\n"
        "    \"context\": \"how this specific symbol appeared in this dream\",\n"
        "    \"associated_emotion\": \"the emotion felt or expressed around this symbol\",\n"
        "    \"user_action\": \"what the dreamer did with or in relation to this symbol\",\n"
        "    \"narrative_effect\": \"how the symbol impacted the dream narrative's flow\",\n"
        "    \"possible_significance\": \"what this contextual combination may suggest psychologically\"\n"
        "  }\n"
        "]\n\n"
        "Output ONLY a valid JSON array. No markdown or wrappers."
    )

    user_prompt = f"Dream: \"{dream_text}\""
    if decomposition:
        user_prompt += f"\nDecomposition: {json.dumps(decomposition)}"
    if db_context:
        user_prompt += f"\n\nHere are database search matches from a dream symbol index for inspiration:\n{db_context}"

    try:
        client = _client()
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},  # Groq JSON mode requires json object root
            temperature=0.2,
            max_tokens=600
        )
        content = (response.choices[0].message.content or "").strip()
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
