from flask import Flask, request, jsonify
import os
import threading
import time

app = Flask(__name__)

# Lazy imports
zsc = None
flan_tok = None
flan_mod = None

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('model_worker')

# Simple file logger for cross-process debugging
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

def log_worker(msg: str):
    ts = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    try:
        with open(os.path.join(LOG_DIR, 'model.log'), 'a', encoding='utf-8') as f:
            f.write(f"{ts} {msg}\n")
    except Exception:
        logger.exception('Failed to write model.log')

@app.route('/status')
def status():
    return jsonify({'zero_shot_loaded': bool(zsc), 'flan_loaded': bool(flan_tok and flan_mod)})

@app.route('/classify', methods=['POST'])
def classify():
    data = request.get_json() or {}
    text = data.get('text')
    if not text:
        return jsonify({'error': 'no text provided'}), 400
    if zsc is None:
        log_worker('Classify called but zero-shot not loaded')
        return jsonify({'error': 'zero-shot model not loaded'}), 503
    try:
        res = zsc(text, os.environ.get('LABEL_CANDIDATES','').split(',') if os.environ.get('LABEL_CANDIDATES') else [] , multi_label=True)
        # Log top labels for visibility
        try:
            labels = res.get('labels', [])
            scores = res.get('scores', [])
            top = ','.join([f"{l}:{s:.2f}" for l,s in zip(labels[:5], scores[:5])])
            log_worker(f'Classify result for snippet "{str(text)[:80]}": {top}')
        except Exception:
            pass
        return jsonify(res)
    except Exception as e:
        logger.exception('classify failed')
        log_worker(f'classify failed: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json() or {}
    dream = data.get('dream')
    labels = data.get('labels') or []
    if flan_tok is None or flan_mod is None:
        log_worker('Generate called but Flan not loaded')
        return jsonify({'error': 'flan model not loaded'}), 503
    try:
        prompt = (
            f"Interpret this dream in psychological terms and provide 2 short suggestions for reflection or coping:\n\n"
            f"Dream: \"{dream}\"\n"
            f"Key indicators: {', '.join(labels)}\n\n"
            f"Response format:\n- Interpretation:\n- Suggestions:\n"
        )
        log_worker(f'Generate request received for dream snippet: {str(dream)[:120]}')
        inputs = flan_tok(prompt, return_tensors='pt')
        outputs = flan_mod.generate(**inputs, max_length=256, do_sample=True, top_p=0.9, temperature=0.7)
        decoded = flan_tok.decode(outputs[0], skip_special_tokens=True).strip()
        if not decoded:
            log_worker(f'Generate produced EMPTY output for dream snippet: {str(dream)[:120]}')
            logger.warning('generate returned empty string')
            return jsonify({'error': 'empty generation output'}), 500
        snippet = decoded.replace('\n',' ')[:300]
        log_worker(f'Generated output length={len(decoded)} preview={snippet}')
        return jsonify({'generated_text': decoded})
    except Exception as e:
        logger.exception('generate failed')
        log_worker(f'generate failed: {e}')
        return jsonify({'error': str(e)}), 500


def load_models():
    global zsc, flan_tok, flan_mod
    try:
        from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
        LABELS = os.environ.get('LABEL_CANDIDATES')
        if LABELS:
            LABEL_CANDIDATES = LABELS.split(',')
        else:
            LABEL_CANDIDATES = [
                "fear","anxiety","stress","freedom","loss","love","relationship",
                "childhood","guilt","success","failure","death","security",
                "travelling","water","animals","work","school","exam","health",
                "family","pregnancy","sex","money","conflict","ambition"
            ]
        try:
            logger.info('Loading zero-shot model in worker...')
            log_worker('Loading zero-shot model in worker...')
            zsc = pipeline('zero-shot-classification', model='facebook/bart-large-mnli')
            logger.info('Zero-shot loaded in worker')
            log_worker('Zero-shot loaded in worker')
        except Exception as e:
            logger.exception('Failed to load zero-shot in worker')
            log_worker(f'Failed to load zero-shot in worker: {e}')
        try:
            logger.info('Loading Flan-T5 in worker...')
            log_worker('Loading Flan-T5 in worker...')
            flan_tok = AutoTokenizer.from_pretrained('google/flan-t5-small')
            flan_mod = AutoModelForSeq2SeqLM.from_pretrained('google/flan-t5-small')
            logger.info('Flan loaded in worker')
            log_worker('Flan loaded in worker')
        except Exception as e:
            logger.exception('Failed to load Flan in worker')
            log_worker(f'Failed to load Flan in worker: {e}')
    except Exception:
        logger.exception('Transformers import failed in worker')

if __name__ == '__main__':
    t = threading.Thread(target=load_models, daemon=True)
    t.start()
    app.run(host='127.0.0.1', port=5010)
