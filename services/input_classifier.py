import json
import logging
from groq_client import safe_groq_completion, GROQ_MODEL, GROQ_API_KEY

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

    stripped = text.strip().lower()

    # 1. Obvious Non-Dream patterns (Math, Code, Weather, Greetings, General QA)
    non_dream_patterns = [
        "hello", "hi", "hey", "how are you", "good morning", "good evening",
        "what is", "who is", "where is", "when did", "calculate", "solve",
        "explain python", "write a code", "write a script", "write a poem", "write code",
        "weather", "forecast", "news today", "stock price", "tell me a joke"
    ]
    if any(stripped.startswith(p) or stripped == p for p in non_dream_patterns):
        # Check if it contains math expression like 2+2
        return {
            "classification": "NON_DREAM",
            "reasoning": "Identified as general query / non-dream input.",
            "confidence": 0.95
        }
    if any(char in stripped for char in ["+", "=", "*", "/"]) and any(c.isdigit() for c in stripped):
        return {
            "classification": "NON_DREAM",
            "reasoning": "Identified as calculation/math query.",
            "confidence": 0.95
        }

    words = stripped.split()
    # 2. Short Ambiguous symbol fragments (1-2 words)
    if len(words) <= 2 and not any(k in stripped for k in ["dream", "nightmare", "slept", "saw", "was"]):
        return {
            "classification": "AMBIGUOUS",
            "reasoning": "Brief symbol or fragment without narrative context.",
            "confidence": 0.85
        }

    # 3. Dream Narrative indicators (>2 words describing subjective dream experience)
    return {
        "classification": "DREAM",
        "reasoning": "Identified as dream narrative.",
        "confidence": 0.92
    }

