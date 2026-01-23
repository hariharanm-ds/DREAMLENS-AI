import os
import requests
from http import HTTPStatus

HUGGINGFACE_TOKEN = os.environ.get('HUGGINGFACE_API_TOKEN')
HF_API = 'https://api-inference.huggingface.co/models/'

# Small helpful label set
LABELS = [
    "fear","anxiety","stress","freedom","loss","love","relationship",
    "childhood","guilt","success","failure","death","security","travelling",
    "water","animals","work","school","exam","health","family","money"
]

headers = {
    'Authorization': f'Bearer {HUGGINGFACE_TOKEN}'
} if HUGGINGFACE_TOKEN else {}


def hf_zero_shot(text, labels):
    # Use HF zero-shot if token present
    if not HUGGINGFACE_TOKEN:
        return []
    payload = {
        'inputs': text,
        'parameters': { 'candidate_labels': labels, 'multi_label': True }
    }
    r = requests.post(HF_API + 'facebook/bart-large-mnli', headers=headers, json=payload, timeout=30)
    if r.status_code != 200:
        return []
    data = r.json()
    res = [lab for lab,score in zip(data.get('labels',[]), data.get('scores',[])) if score>0.15]
    return res[:6]


def hf_generate(dream, labels):
    if not HUGGINGFACE_TOKEN:
        return None
    prompt = f"Interpret this dream in psychological terms and provide 2 short suggestions:\nDream: '{dream}'\nKey indicators: {', '.join(labels)}\n"
    r = requests.post(HF_API + 'google/flan-t5-small', headers=headers, json={'inputs':prompt}, timeout=60)
    if r.status_code != 200:
        return None
    out = r.json()
    # HF returns list of strings or dict depending on model, handle common cases
    if isinstance(out, list) and out:
        return out[0].get('generated_text') if isinstance(out[0], dict) else out[0]
    if isinstance(out, dict) and 'generated_text' in out:
        return out['generated_text']
    return None


# Vercel-serverless handler

def handler(request):
    try:
        body = request.get_json(silent=True) or {}
        dream = (body.get('dream') or '').strip()
        if not dream:
            return ({'success': False, 'message': 'No dream provided'}, HTTPStatus.BAD_REQUEST)

        labels = hf_zero_shot(dream, LABELS)
        gen = hf_generate(dream, labels)
        if gen:
            return ({'success': True, 'dream': dream, 'labels': labels, 'interpretation': gen}, HTTPStatus.OK)
        # fallback simple text:
        fallback = f"This dream seems related to {', '.join(labels) if labels else 'some themes'}. Try journaling about people and locations to explore more." 
        return ({'success': True, 'dream': dream, 'labels': labels, 'interpretation': fallback}, HTTPStatus.OK)
    except Exception as e:
        return ({'success': False, 'message': str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR)