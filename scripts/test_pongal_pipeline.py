import sys
sys.path.insert(0, 'e:/DreamLensAI')
from services.pipeline import run_dream_pipeline

result = run_dream_pipeline("I was celebrating pongal with my family")
print("Classification:", result.get("classification"))
in_short = result.get("in_short", {})
print("Summary:", in_short.get("summary"))
print("\nRevelation snippet:")
print(in_short.get("revelation")[:300])
print("\nTakeaway:", in_short.get("takeaway"))

# Check for bad words like 'fear', 'threat', 'avoidance'
rev_lower = (in_short.get("revelation") or "").lower()
print("\nHas 'fear' in revelation?", 'fear' in rev_lower)
print("Has 'threat' in revelation?", 'threat' in rev_lower)
print("Has 'abundance' in revelation?", 'abundance' in rev_lower)
