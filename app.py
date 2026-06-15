from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
import random
from functools import lru_cache
import sys
from datetime import datetime

# Ollama Llama 3 integration
from ollama_client import interpret_dream as ollama_interpret, check_ollama_health

# Runtime configuration
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)


def log_model(msg: str):
    ts = datetime.utcnow().isoformat()
    try:
        with open(os.path.join(LOG_DIR, "model.log"), "a", encoding="utf-8") as f:
            f.write(f"{ts} {msg}\n")
    except Exception:
        # best-effort logging, don't crash the app
        print(f"LOG FAIL: {msg}")

# NLP libraries for dataset matching (lightweight, no torch needed)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# ---------- Fallback responses (used when Ollama is unavailable) ----------
fallback_responses = [
    "Dreams about {topic} can reflect a desire for transformation or escape from daily stress. It might be your mind signaling the need for change.",
    "When you dream of {topic}, it often symbolizes emotional shifts or inner awakening. Consider what's been changing in your life recently.",
    "This dream suggests that your subconscious is processing a deep thought or event. Pay attention to your emotions connected with {topic}.",
    "It could represent your journey through unknown territories in life. Embrace it with courage — something beautiful might be ahead.",
    "This may point toward unresolved thoughts or future possibilities. It's your mind's way of helping you grow stronger mentally."
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

# ---------- Dataset matching ----------

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


def search_database_context(dream_text: str) -> str:
    """Search the dream database for related symbols to provide context to Llama 3."""
    if dreams_df.empty:
        return ""
    dream_words = dream_text.lower().split()
    results = []
    for _, row in dreams_df.iterrows():
        word = str(row["Word"]).lower()
        matches = sum(1 for w in dream_words if w in word or word in w)
        if matches > 0:
            results.append({
                "word": row["Word"],
                "interpretation": str(row["Interpretation"])[:150],
                "relevance": matches
            })
    results.sort(key=lambda x: x["relevance"], reverse=True)
    if not results:
        return ""
    context_parts = []
    for r in results[:3]:
        context_parts.append(f"- {r['word']}: {r['interpretation']}...")
    return "\n".join(context_parts)


def synthesize_fallback(dream: str) -> str:
    """Produce a friendly template fallback when Ollama is unavailable."""
    # Extract a simple topic from the dream
    words = [w for w in dream.split() if len(w) > 3]
    topic = ", ".join(words[:3]) if words else "your dream"
    template = random.choice(fallback_responses)
    return template.format(topic=topic)


# ---------- Flask Routes ----------

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


# ---------- Main Interpret Endpoint ----------

@app.route("/interpret", methods=["POST"])
def interpret():
    data = request.get_json() or {}
    dream = (data.get("dream") or "").strip()
    if not dream:
        return jsonify({"success": False, "message": "Please provide a dream text."}), 400

    # Allow caller to force LLM generation (skip dataset match)
    force_model = bool(data.get('force_model', False))

    # 1) Try dataset match first (fast, no LLM call)
    if not force_model:
        structured = find_best_match_simple(dream.lower())
    else:
        structured = None

    if structured:
        interpretation_text = structured['interpretation']
        meta = {"method": "dataset", "score": structured['score']}
    else:
        # 2) Call Ollama Llama 3 for AI interpretation
        db_context = search_database_context(dream)
        ollama_result = ollama_interpret(dream, db_context=db_context)

        if ollama_result["success"]:
            interpretation_text = ollama_result["interpretation"]
            meta = {"method": "llama3", "model": ollama_result["model"]}
        else:
            # 3) Fallback if Ollama is unavailable
            log_model(f"Ollama failed: {ollama_result['error']}")
            interpretation_text = synthesize_fallback(dream)
            meta = {
                "method": "fallback",
                "ollama_error": ollama_result["error"],
                "note": "Ollama is not available. Please ensure Ollama is running with Llama 3."
            }

    # mark whether the client forced model usage
    meta['forced'] = force_model

    result = {
        "success": True,
        "dream": dream,
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


# --- UI pages ---
@app.route('/about')
def about_page():
    return render_template('about.html')

@app.route('/contact')
def contact_page():
    return render_template('contact.html')

@app.route('/history')
def history_page():
    return render_template('history.html')

# --- Admin UI ---
@app.route('/admin')
def admin_page():
    ollama_status = check_ollama_health()
    # read last 200 lines of model.log for quick debugging
    log_lines = []
    try:
        with open(os.path.join(LOG_DIR, 'model.log'), 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()
            log_lines = lines[-200:]
    except Exception:
        log_lines = ['No logs yet.']
    return render_template('admin.html', ollama=ollama_status, logs=log_lines)

@app.route('/admin/reload_models', methods=['POST'])
def admin_reload_models():
    """Check Ollama status and report."""
    try:
        status = check_ollama_health()
        return jsonify({'success': True, 'status': status})
    except Exception as e:
        log_model(f"admin_reload_models error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/admin/start_worker', methods=['POST'])
def admin_start_worker():
    """Ollama runs as an external process; this just checks its status."""
    status = check_ollama_health()
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
    ollama = check_ollama_health()
    return jsonify({
        'status': 'ok',
        'ollama': ollama
    })

@app.route('/_model_status')
def model_status():
    try:
        status = check_ollama_health()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/_env_check')
def env_check():
    try:
        # Check for key runtime dependencies without crashing the app
        modules = ['sklearn', 'pandas', 'requests']
        info = {}
        for m in modules:
            try:
                mod = __import__(m)
                ver = getattr(mod, '__version__', 'unknown')
                info[m] = {'installed': True, 'version': str(ver)}
            except Exception as e:
                info[m] = {'installed': False, 'error': str(e)}
        info['python_version'] = sys.version
        info['ollama'] = check_ollama_health()
        return jsonify(info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    # Print startup info (ASCII-safe for Windows cp1252 consoles)
    print("=" * 60)
    print("  DREAMLENS AI -- Powered by Ollama Llama 3")
    print("=" * 60)

    ollama = check_ollama_health()
    if ollama["connected"]:
        print(f"  [OK] Ollama connected at {os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')}")
        print(f"  [MODELS] Available: {', '.join(ollama['models']) or 'none'}")
        if ollama["llama3_available"]:
            print("  [READY] Llama 3 is ready!")
        else:
            print("  [WARN] Llama 3 not found. Run: ollama pull llama3")
    else:
        print(f"  [ERROR] Ollama is not running: {ollama['error']}")
        print("  [TIP] Start Ollama with: ollama serve")
        print("  [TIP] Then pull Llama 3: ollama pull llama3")

    print(f"  [DATA] Dream database: {len(dreams_df)} entries loaded")
    print("=" * 60)
    print(f"  [SERVER] Starting on http://127.0.0.1:{port}")
    print("=" * 60)

    # On Windows the Flask reloader can cause socket issues; disable it by default here.
    import platform
    kwargs = dict(host="127.0.0.1", port=port, debug=False, use_reloader=False)
    app.run(**kwargs)
