import time, json
from groq_client import _client

client = _client()

msgs = [
    {"role": "system", "content": "You are a JSON API. Return valid JSON only."},
    {"role": "user", "content": 'Analyze dream: A lion chased me through golden fire. Return {"center_node": "Lion", "summary": "meaning", "emotion": "fear"}'}
]

for model in ["groq/compound", "groq/compound-mini", "qwen/qwen3.8-27b"]:
    t0 = time.time()
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=msgs,
            response_format={"type": "json_object"},
            max_tokens=200,
            temperature=0.3
        )
        t1 = time.time()
        content = resp.choices[0].message.content
        parsed = json.loads(content)
        print(f"OK {model}: {t1-t0:.2f}s | {list(parsed.keys())}")
    except Exception as e:
        t1 = time.time()
        err = str(e)[:120]
        print(f"FAIL {model}: {t1-t0:.2f}s | {err}")
