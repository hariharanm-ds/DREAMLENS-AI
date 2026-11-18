with open('services/pipeline.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update generate_rich_revelation in services/pipeline.py
old_revelation_start = 'def generate_rich_revelation(dream_text: str, primary_theme: str = None, key_symbols: list = None, tone: str = None) -> str:'
new_revelation_case = '''def generate_rich_revelation(dream_text: str, primary_theme: str = None, key_symbols: list = None, tone: str = None) -> str:
    """
    Generates a longer, deeply engaging, fascinating multi-paragraph psychological
    narrative revelation for the dream instead of a static motivational quote.
    """
    text_lower = (dream_text or "").lower()
    symbols_str = ", ".join(key_symbols) if key_symbols else "your core dream symbols"
    theme_str = primary_theme or "Personal Sovereignty & Inner Alignment"

    if any(k in text_lower for k in ["pongal", "diwali", "festival", "harvest", "feast", "celebrat", "sugarcane", "pot", "boiled", "sweet", "family"]):
        return (
            "Your dream reflects a soul-nourishing celebration of sacred abundance, gratitude, and familial harmony. "
            "In subconscious symbolism, harvest festivals like Pongal embody the profound spiritual truth of 'overflowing prosperity' "
            "(Pongalo Pongal!)—where nature, solar warmth, and ancestral traditions unite in joyful thanksgiving.\\n\\n"
            "This vision is an auspicious affirmation from your deeper mind: your psyche is feeling grounded, deeply connected to your roots, "
            "and receptive to new blessings. The traditional boiling over of milk and rice represents life's gifts overflowing beyond the narrow boundaries "
            "of daily worry, signifying that your efforts are yielding sweetness and shared joy.\\n\\n"
            "This dream carries no threat or fear—it is a sacred invitation to celebrate the abundance already present in your waking life. "
            "Honor your family bonds, express heartfelt gratitude for the quiet blessings around you, and remember that true prosperity multiplies "
            "infinitely when shared with warmth and generosity."
        )'''

if old_revelation_start in text:
    # Find start and replace through the first if
    idx1 = text.find(old_revelation_start)
    idx2 = text.find('if any(k in text_lower for k in ["elephant"', idx1)
    if idx2 != -1:
        text = text[:idx1] + new_revelation_case + "\n    el" + text[idx2:]
        print("Added celebration / Pongal case to generate_rich_revelation!")
    else:
        print("WARNING: elephant check not found.")
else:
    print("WARNING: generate_rich_revelation not found.")

# 2. Update simulate_scenario_pipeline prompt
old_sim_prompt_rule = "Generate an inspiring alternative timeline narrative, 4 concrete possible outcomes/empowerments, and a visual artwork description.\n\n"
new_sim_prompt_rule = (
    "Generate an inspiring alternative timeline narrative, 4 concrete possible outcomes/empowerments, and a visual artwork description.\n\n"
    "CRITICAL RULE FOR EMOTIONAL TONE & CONTEXT:\n"
    "Match the tone to the dream's actual nature. If the dream is a joyful festival, celebration, or harvest (e.g. Pongal, Diwali, wedding, feast), "
    "DO NOT invent anxiety, fear, threat, or avoidance! Write an alternative timeline celebrating overflowing abundance, ancestral blessings, and community joy. "
    "Only discuss confronting fear if the original dream actually contained a threat or nightmare.\n\n"
)

if old_sim_prompt_rule in text and new_sim_prompt_rule not in text:
    text = text.replace(old_sim_prompt_rule, new_sim_prompt_rule, 1)
    print("Updated simulate_scenario_pipeline system prompt with tone awareness!")

with open('services/pipeline.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Saved services/pipeline.py successfully.")
