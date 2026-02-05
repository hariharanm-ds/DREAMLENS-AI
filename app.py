from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
import random
from functools import lru_cache
import sys
from datetime import datetime

# Runtime configuration
USE_HF_ONLY = os.environ.get("USE_HF_ONLY", "0").lower() in ("1", "true", "yes")
RUNTIME_CONFIG = 'config/runtime.json'
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(os.path.dirname(RUNTIME_CONFIG), exist_ok=True)

# Keep runtime JSON for a persistent flag that can be toggled via the admin UI
def _read_runtime_config():
    try:
        import json
        if os.path.exists(RUNTIME_CONFIG):
            with open(RUNTIME_CONFIG, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print('Failed to read runtime config:', e)
    return {'use_hf_only': USE_HF_ONLY}

def _write_runtime_config(cfg: dict):
    try:
        import json
        with open(RUNTIME_CONFIG, 'w', encoding='utf-8') as f:
            json.dump(cfg, f)
        return True
    except Exception as e:
        print('Failed to write runtime config:', e)
        return False


def log_model(msg: str):
    ts = datetime.utcnow().isoformat()
    try:
        with open(os.path.join(LOG_DIR, "model.log"), "a", encoding="utf-8") as f:
            f.write(f"{ts} {msg}\n")
    except Exception:
        # best-effort logging, don't crash the app
        print(f"LOG FAIL: {msg}")

# NLP & ML libraries (models are lazy-loaded)
# Avoid importing heavy transformer modules at top-level to speed service startup.
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# ---------- Embedded model worker (background thread, no separate process) ----------
import threading
import time

_worker_models = {'zsc': None, 'flan_tok': None, 'flan_mod': None}
_worker_ready = threading.Event()

def _load_models_in_thread():
    """Load transformer models in a background thread to avoid blocking Flask startup."""
    try:
        from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
        try:
            log_model('Loading zero-shot in background...')
            _worker_models['zsc'] = pipeline('zero-shot-classification', model='facebook/bart-large-mnli')
            log_model('Zero-shot loaded in background')
        except Exception as e:
            log_model(f'Failed to load zero-shot: {e}')
        try:
            log_model('Loading Flan-T5 in background...')
            _worker_models['flan_tok'] = AutoTokenizer.from_pretrained('google/flan-t5-small')
            _worker_models['flan_mod'] = AutoModelForSeq2SeqLM.from_pretrained('google/flan-t5-small')
            log_model('Flan-T5 loaded in background')
        except Exception as e:
            log_model(f'Failed to load Flan-T5: {e}')
    except Exception as e:
        log_model(f'Failed to import transformers: {e}')
    finally:
        _worker_ready.set()

# Start background loader thread on app startup
_loader_thread = threading.Thread(target=_load_models_in_thread, daemon=True)
_loader_thread.start()

def get_worker_zsc():
    """Get the zero-shot classifier (waits for background load if needed)."""
    _worker_ready.wait(timeout=30)
    return _worker_models.get('zsc')

def get_worker_flan():
    """Get the Flan-T5 tokenizer and model (waits for background load if needed)."""
    _worker_ready.wait(timeout=30)
    tok = _worker_models.get('flan_tok')
    mod = _worker_models.get('flan_mod')
    return tok, mod

# ---------- Fallback responses (simple, fast) ----------
fallback_responses = [
    "Dreams about {topic} can reflect a desire for transformation or escape from daily stress. It might be your mind signaling the need for change.",
    "When you dream of {topic}, it often symbolizes emotional shifts or inner awakening. Consider what’s been changing in your life recently.",
    "This dream suggests that your subconscious is processing a deep thought or event. Pay attention to your emotions connected with {topic}.",
    "It could represent your journey through unknown territories in life. Embrace it with courage — something beautiful might be ahead.",
    "This may point toward unresolved thoughts or future possibilities. It’s your mind’s way of helping you grow stronger mentally."
]

# ---------- Load structured dataset (optional) ----------

def load_data():
    try:
        df = pd.read_csv("project/cleaned_dream_interpretations.csv")
        if "Word" not in df.columns or "Interpretation" not in df.columns:
            return pd.DataFrame(columns=["Word", "Interpretation"])
        return df
    except Exception as e:
        print("No dataset found or failed to load:", e)
        return pd.DataFrame(columns=["Word", "Interpretation"])

dreams_df = load_data()
if not dreams_df.empty:
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(dreams_df["Word"].astype(str))
else:
    vectorizer = None
    tfidf_matrix = None

# Predefined label candidates for zero-shot classification
LABEL_CANDIDATES = [
    "fear", "anxiety", "stress", "freedom", "loss", "love", "relationship",
    "childhood", "guilt", "success", "failure", "death", "security",
    "travelling", "water", "animals", "work", "school", "exam", "health",
    "family", "pregnancy", "sex", "money", "conflict", "ambition"
]

# Helper functions

@lru_cache(maxsize=512)
def find_best_match_simple(text: str):
    """Find best match from the dataset using TF-IDF similarity (if available)."""
    if vectorizer is None or tfidf_matrix is None or dreams_df.empty:
        return None
    user_vector = vectorizer.transform([text])
    sims = cosine_similarity(user_vector, tfidf_matrix).flatten()
    idx = sims.argmax()
    score = sims[idx]
    if score > 0.35:
        return {
            "interpretation": dreams_df.iloc[idx]["Interpretation"],
            "score": float(score)
        }
    return None


def is_garbage_generation(text: str) -> bool:
    """Simple heuristics to detect obviously malformed or repetitive outputs from the model."""
    if not text:
        return True
    t = text.strip()
    if len(t) < 25:
        return True
    low = t.lower()
    if 'id :' in low or 'id:' in low:
        return True
    words = [w for w in t.split() if any(c.isalnum() for c in w)]
    if not words:
        return True
    unique_ratio = len(set(words)) / max(1, len(words))
    if unique_ratio < 0.25:
        return True
    # detect long repeated substrings
    for k in range(1,6):
        # k-word n-gram repetition
        grams = [' '.join(words[i:i+k]) for i in range(0, len(words)-k+1)]
        for g in set(grams):
            if grams.count(g) > 6:
                return True
    return False


def synthesize_fallback(dream: str, labels: list) -> str:
    """Produce a friendly template fallback using detected labels when model output is unavailable."""
    label_text = ", ".join(labels[:5]) if labels else "general emotions"
    return (
        f"This dream seems related to {label_text}. It may reflect your current emotional state or recent experiences. "
        f"Try journaling about who, what, and where in your dream to gain clarity. Suggestions: 1) Note how the symbol made you feel. "
        f"2) Spend 5 minutes writing about any real-life parallels."
    )

def _call_hf_inference(prompt: str):
    """Call Hugging Face Inference API for generation if HUGGINGFACE_API_TOKEN is set."""
    token = os.environ.get("HUGGINGFACE_API_TOKEN")
    if not token:
        return None
    url = "https://api-inference.huggingface.co/models/google/flan-t5-small"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 200, "do_sample": True, "top_p": 0.9, "temperature": 0.7}
    }
    try:
        import requests
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        # HF returns [{'generated_text': '...'}] for text-generation models
        if isinstance(data, dict) and data.get("error"):
            print("HF inference error:", data.get("error"))
            return None
        if isinstance(data, list) and len(data) > 0:
            out = data[0].get("generated_text") or data[0].get("text") or None
            if out:
                return out.strip()
        if isinstance(data, str):
            return data.strip()
    except Exception as e:
        print("Hugging Face inference call failed:", e)
    return None


def generate_interpretation_with_flan(dream_text: str, labels: list[str]):
    """Generate a human-readable interpretation using Flan-T5 prompt, with HF fallback and optional forced HF mode."""
    prompt = (
        f"Interpret this dream in psychological terms and provide 2 short suggestions for reflection or coping:\n\n" 
        f"Dream: \"{dream_text}\"\n" 
        f"Key indicators: {', '.join(labels)}\n\n" 
        f"Response format:\n- Interpretation:\n- Suggestions:\n"
    )

    # If the operator set USE_HF_ONLY (env or runtime config), prefer HF remote inference
    cfg = _read_runtime_config()
    if cfg.get('use_hf_only'):
        log_model("USE_HF_ONLY set in runtime config — calling HF inference API")
        hf_out = _call_hf_inference(prompt)
        if hf_out:
            log_model("HF inference used due to USE_HF_ONLY")
            return hf_out
        else:
            log_model("USE_HF_ONLY set but HF inference call failed — falling through to local/template fallback")
def generate_interpretation_with_flan(dream_text: str, labels: list[str]):
    """Generate interpretation using embedded Flan-T5 (loaded in background thread)."""
    prompt = (
        f"Interpret this dream in psychological terms and provide 2 short suggestions for reflection or coping:\n\n" 
        f"Dream: \"{dream_text}\"\n" 
        f"Key indicators: {', '.join(labels)}\n\n" 
        f"Response format:\n- Interpretation:\n- Suggestions:\n"
    )

    # If the operator set USE_HF_ONLY, prefer HF remote inference
    cfg = _read_runtime_config()
    if cfg.get('use_hf_only'):
        log_model("USE_HF_ONLY set in runtime config — calling HF inference API")
        hf_out = _call_hf_inference(prompt)
        if hf_out:
            log_model("HF inference used due to USE_HF_ONLY")
            return hf_out
        else:
            log_model("USE_HF_ONLY set but HF inference call failed — falling through")

    # Try to use embedded Flan-T5 from background thread
    try:
        flan_tok, flan_mod = get_worker_flan()
        if flan_tok is not None and flan_mod is not None:
            inputs = flan_tok(prompt, return_tensors="pt")
            outputs = flan_mod.generate(**inputs, max_length=200, do_sample=True, top_p=0.9, temperature=0.7)
            decoded = flan_tok.decode(outputs[0], skip_special_tokens=True)
            return decoded.strip()
    except Exception as e:
        msg = f"Embedded Flan-T5 generation failed: {e}"
        print(msg)
        log_model(msg)

    # Fallback to Hugging Face Inference API if token is provided
    hf_out = _call_hf_inference(prompt)
    if hf_out:
        log_model("Using Hugging Face Inference API fallback for generation.")
        return hf_out

    # Last-resort template fallback
    label_text = ", ".join(labels[:5]) if labels else "general emotions"
    fallback = f"This dream seems related to {label_text}. It may reflect your current emotional state, unresolved feelings, or recent experiences. Try journaling about who, what, and where in your dream to gain clarity."
    log_model("All generation methods failed — returning template fallback.")
    return fallback

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat")
def chat():
    return render_template("chat.html")

@app.route("/annotate")
def annotate_ui():
    return render_template("annotate.html")

# Simple annotation storage (append CSV)
import csv
from datetime import datetime

ANNOTATION_FILE = 'data/annotations.csv'

@app.route('/annotations', methods=['POST'])
def save_annotation():
    payload = request.get_json() or {}
    dream = (payload.get('dream') or '').strip()
    labels = payload.get('labels') or []
    note = payload.get('note') or ''
    if not dream:
        return jsonify({'success': False, 'message': 'No dream provided'}), 400
    # ensure folder
    os.makedirs(os.path.dirname(ANNOTATION_FILE), exist_ok=True)
    with open(ANNOTATION_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.utcnow().isoformat(), dream, '|'.join(labels), note])
    return jsonify({'success': True})

@app.route('/annotations/recent')
def recent_annotations():
    recent = []
    try:
        with open(ANNOTATION_FILE, 'r', encoding='utf-8') as f:
            rows = list(csv.reader(f))[-20:]
            for r in reversed(rows):
                ts, dream, labs, note = r
                recent.append({'ts': ts, 'dream': dream, 'labels': labs.split('|') if labs else [], 'note': note})
    except FileNotFoundError:
        recent = []
    return jsonify({'recent': recent})


@app.route("/interpret", methods=["POST"])
def interpret():
    data = request.get_json() or {}
    dream = (data.get("dream") or "").strip()
    if not dream:
        return jsonify({"success": False, "message": "Please provide a dream text."}), 400

    # Allow caller to force model generation (skip dataset match)
    force_model = bool(data.get('force_model', False))
    if force_model:
        structured = None
    else:
        structured = find_best_match_simple(dream.lower())

    # 2) Zero-shot labels
    labels = []
    try:
        cfg = _read_runtime_config()
        if not cfg.get('use_hf_only'):
            zsc = get_worker_zsc()
            if zsc is not None:
                zsc_res = zsc(dream, LABEL_CANDIDATES, multi_label=True)
                labels = [lab for lab, score in zip(zsc_res['labels'], zsc_res['scores']) if score > 0.20][:6]
    except Exception as e:
        print("Zero-shot classification error:", e)
        log_model(f"Zero-shot error: {e}")

    # 3) Generate explanation
    interpretation_text = ""
    if structured:
        interpretation_text = structured['interpretation']
        meta = {"method": "dataset", "score": structured['score']}
    else:
        # Generation: use embedded worker models
        cfg = _read_runtime_config()
        gen_text = None
        if not cfg.get('use_hf_only'):
            try:
                flan_tok, flan_mod = get_worker_flan()
                if flan_tok is not None and flan_mod is not None:
                    prompt = (
                        f"Interpret this dream in psychological terms and provide 2 short suggestions for reflection or coping:\n\n"
                        f"Dream: \"{dream}\"\n"
                        f"Key indicators: {', '.join(labels)}\n\n"
                        f"Response format:\n- Interpretation:\n- Suggestions:\n"
                    )
                    inputs = flan_tok(prompt, return_tensors="pt")
                    outputs = flan_mod.generate(**inputs, max_length=256, do_sample=True, top_p=0.9, temperature=0.7)
                    gen_text = flan_tok.decode(outputs[0], skip_special_tokens=True).strip()
                    if is_garbage_generation(gen_text):
                        log_model('Generated output was malformed; using synthesized fallback.')
                        gen_text = synthesize_fallback(dream, labels)
                        interpretation_text = gen_text
                        meta = {"method": "flan-t5-fallback", "labels": labels, "gen_loaded": False}
                    else:
                        interpretation_text = gen_text
                        meta = {"method": "flan-t5", "labels": labels, "gen_loaded": True}
            except Exception as e:
                log_model(f"Flan generation failed: {e}")
        if gen_text is None:
            # Fallback: use HF inference
            interpretation_text = _call_hf_inference(prompt) or synthesize_fallback(dream, labels)
            meta = {"method": "hf-inference", "labels": labels}

    # mark whether the client forced model usage
    meta['forced'] = force_model

    result = {
        "success": True,
        "dream": dream,
        "labels": labels,
        "interpretation": interpretation_text,
        "meta": meta
    }

    # Store to history (sqlite) for user reference
    try:
        import sqlite3
        os.makedirs('data', exist_ok=True)
        conn = sqlite3.connect('data/history.db')
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS history (ts TEXT, dream TEXT, response TEXT)''')
        cur.execute('INSERT INTO history (ts,dream,response) VALUES (?,?,?)', (datetime.utcnow().isoformat(), dream, interpretation_text))
        conn.commit()
        conn.close()
    except Exception as e:
        print('Failed to save history:', e)

    return jsonify(result)

@app.route('/history/recent')
def history_recent():
    items = []
    try:
        import sqlite3
        conn = sqlite3.connect('data/history.db')
        cur = conn.cursor()
        cur.execute('SELECT ts,dream,response FROM history ORDER BY rowid DESC LIMIT 25')
        rows = cur.fetchall()
        for r in rows:
            items.append({'ts': r[0], 'dream': r[1], 'response': r[2]})
        conn.close()
    except Exception as e:
        print('Failed to read history:', e)
    return jsonify({'items': items})


# --- UI pages missing earlier ---
@app.route('/about')
def about_page():
    return render_template('about.html')

@app.route('/contact')
def contact_page():
    return render_template('contact.html')

@app.route('/history')
def history_page():
    return render_template('history.html')

# --- Admin UI to toggle runtime options (e.g., force HF-only mode) ---
@app.route('/admin')
def admin_page():
    cfg = _read_runtime_config()
    # read last 200 lines of model.log for quick debugging
    log_lines = []
    try:
        with open(os.path.join(LOG_DIR, 'model.log'), 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()
            log_lines = lines[-200:]
    except Exception:
        log_lines = ['No logs yet.']
    return render_template('admin.html', cfg=cfg, logs=log_lines)

@app.route('/admin/set_hf_only', methods=['POST'])
def admin_set_hf_only():
    payload = request.get_json() or {}
    val = bool(payload.get('use_hf_only'))
    cfg = _read_runtime_config()
    cfg['use_hf_only'] = val
    ok = _write_runtime_config(cfg)
    if not ok:
        return jsonify({'success': False, 'message': 'Failed to write runtime config.'}), 500
    log_model(f"Admin set use_hf_only = {val}")
    return jsonify({'success': True, 'use_hf_only': val})

@app.route('/admin/reload_models', methods=['POST'])
def admin_reload_models():
    """Report status of embedded models (loaded in background thread)."""
    try:
        # Check if models are loaded
        zsc = get_worker_zsc()
        flan_tok, flan_mod = get_worker_flan()
        
        status = {
            'zero_shot_loaded': bool(zsc),
            'flan_loaded': bool(flan_tok and flan_mod),
            'note': 'Models are loaded in a background thread. If not loaded yet, please wait and retry.'
        }
        return jsonify({'success': True, 'status': status})
    except Exception as e:
        log_model(f"admin_reload_models error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/admin/start_worker', methods=['POST'])
def admin_start_worker():
    """Models are embedded; no separate worker process needed."""
    zsc = get_worker_zsc()
    flan_tok, flan_mod = get_worker_flan()
    status = {
        'zero_shot_loaded': bool(zsc),
        'flan_loaded': bool(flan_tok and flan_mod),
        'note': 'Models are loaded in background. If still loading, please wait.'
    }
    return jsonify({'success': True, 'status': status})

@app.route('/contact/submit', methods=['POST'])
def contact_submit():
    payload = request.get_json() or {}
    name = (payload.get('name') or '').strip()
    email = (payload.get('email') or '').strip()
    message = (payload.get('message') or '').strip()
    if not message:
        return jsonify({'success': False, 'message': 'No message provided'}), 400
    os.makedirs('data', exist_ok=True)
    try:
        with open('data/contacts.csv', 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([datetime.utcnow().isoformat(), name, email, message])
    except Exception as e:
        print('Failed to save contact:', e)
        return jsonify({'success': False, 'message': 'Failed to save contact'}), 500
    return jsonify({'success': True})

@app.route('/_health')
def health_check():
    return jsonify({'status': 'ok'})

@app.route('/_model_status')
def model_status():
    try:
        hf_token_present = bool(os.environ.get('HUGGINGFACE_API_TOKEN'))
        # Check embedded model thread status
        zsc = get_worker_zsc()
        flan_tok, flan_mod = get_worker_flan()
        return jsonify({
            'zero_shot_loaded': bool(zsc),
            'flan_loaded': bool(flan_tok and flan_mod),
            'hf_token_present': hf_token_present,
            'note': 'Models load in background thread; check status in admin page.'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/_env_check')
def env_check():
    try:
        # Check for key runtime dependencies without crashing the app
        modules = ['torch', 'transformers', 'sklearn', 'pandas', 'requests']
        info = {}
        for m in modules:
            try:
                mod = __import__(m)
                ver = getattr(mod, '__version__', 'unknown')
                info[m] = {'installed': True, 'version': str(ver)}
            except Exception as e:
                err = str(e)
                info[m] = {'installed': False, 'error': err}
                # Add helpful hint for common torch Windows DLL errors
                if m == 'torch' and ('c10' in err or 'WinError' in err or 'DLL' in err):
                    info[m]['hint'] = 'Windows DLL init failure detected. Try installing CPU-only PyTorch: scripts/install_cpu_torch.ps1 (Windows) or scripts/install_cpu_torch.sh (Linux/Mac). Alternatively set USE_HF_ONLY=1 and add HUGGINGFACE_API_TOKEN to use remote inference.'
        info['python_version'] = sys.version
        info['use_hf_only'] = USE_HF_ONLY
        info['hf_token_present'] = bool(os.environ.get('HUGGINGFACE_API_TOKEN'))
        # Check if model worker is running
        try:
            import requests
            r = requests.get('http://127.0.0.1:5010/status', timeout=1)
            if r.ok:
                info['model_worker'] = r.json()
            else:
                info['model_worker'] = None
        except Exception:
            info['model_worker'] = None
        return jsonify(info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # On Windows the Flask reloader can cause socket issues; disable it by default here.
    import platform
    kwargs = dict(host="127.0.0.1", port=port, debug=False, use_reloader=False)
    app.run(**kwargs)
