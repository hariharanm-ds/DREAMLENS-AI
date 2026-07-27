from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
import random
from functools import lru_cache
import sys
import tempfile
from datetime import datetime

# Groq Llama integration
from groq_client import interpret_dream as groq_interpret, check_groq_health
from services.pipeline import run_dream_pipeline, run_refinement_pipeline, run_comparison_pipeline

# Runtime configuration
IS_VERCEL = bool(os.environ.get("VERCEL"))
TMP_DIR = tempfile.gettempdir()
LOG_DIR = os.environ.get("LOG_DIR", os.path.join(TMP_DIR, "dreamlens-logs") if IS_VERCEL else "logs")
DATA_DIR = os.environ.get("DATA_DIR", os.path.join(TMP_DIR, "dreamlens-data") if IS_VERCEL else "data")


def ensure_dir(path: str):
    try:
        os.makedirs(path, exist_ok=True)
    except Exception:
        # Vercel's project filesystem can be read-only. Route handlers still use
        # best-effort logging/storage and should not fail app import.
        pass


ensure_dir(LOG_DIR)
ensure_dir(DATA_DIR)


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

# ---------- Fallback responses (used when Groq is unavailable) ----------
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
    """Search the dream database for related symbols to provide context to the model."""
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
    """Produce a friendly template fallback when Groq is unavailable."""
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

ANNOTATION_FILE = os.path.join(DATA_DIR, 'annotations.csv')

@app.route('/annotations', methods=['POST'])
def save_annotation():
    payload = request.get_json() or {}
    dream = (payload.get('dream') or '').strip()
    labels = payload.get('labels') or []
    note = payload.get('note') or ''
    if not dream:
        return jsonify({'success': False, 'message': 'No dream provided'}), 400
    # ensure folder
    ensure_dir(os.path.dirname(ANNOTATION_FILE))
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

def format_report_as_markdown(report_dict, hypotheses=None) -> str:
    parts = []
    if report_dict.get("atmosphere"):
        parts.append(f"🌙 **DREAM ATMOSPHERE**\n\n{report_dict['atmosphere']}\n")
    if report_dict.get("story_map"):
        parts.append(f"📖 **DREAM STORY MAP**\n\n{report_dict['story_map']}\n")
    if report_dict.get("emotional_arc_text"):
        parts.append(f"📊 **EMOTIONAL ARC**\n\n{report_dict['emotional_arc_text']}\n")
    if report_dict.get("symbol_relationships_text"):
        parts.append(f"🔍 **KEY SYMBOL RELATIONSHIPS**\n\n{report_dict['symbol_relationships_text']}\n")
    if report_dict.get("central_tension"):
        parts.append(f"⚡ **THE CENTRAL TENSION**\n\n{report_dict['central_tension']}\n")
    
    lenses = report_dict.get("psychological_lenses", {})
    if lenses:
        parts.append("🧠 **PSYCHOLOGICAL LENSES**\n")
        if lenses.get("emotional_psychology"):
            parts.append(f"- *Emotional Psychology:* {lenses['emotional_psychology']}")
        if lenses.get("jungian_lens"):
            parts.append(f"- *Jungian Perspective:* {lenses['jungian_lens']}")
        if lenses.get("narrative_psychology"):
            parts.append(f"- *Narrative Analysis:* {lenses['narrative_psychology']}")
        if lenses.get("personal_growth"):
            parts.append(f"- *Personal Growth:* {lenses['personal_growth']}")
        parts.append("")
        
    if hypotheses:
        parts.append("🔮 **POSSIBLE INTERPRETATIONS (HYPOTHESES)**\n")
        for idx, h in enumerate(hypotheses):
            parts.append(f"**Interpretation {idx+1}: {h.get('title')}**")
            parts.append(f"- *Explanation:* {h.get('explanation')}")
            parts.append(f"- *Evidence:* {h.get('evidence')}")
            parts.append(f"- *Confidence:* {h.get('confidence')}")
            parts.append(f"- *Validation Condition:* {h.get('validation_condition')}\n")
            
    if report_dict.get("mythological_reflection"):
        parts.append(f"🕉️ **MYTHOLOGICAL REFLECTION**\n\n{report_dict['mythological_reflection']}\n")
    if report_dict.get("what_mind_exploring"):
        parts.append(f"✨ **WHAT YOUR MIND MAY BE EXPLORING**\n\n{report_dict['what_mind_exploring']}\n")
        
    qs = report_dict.get("reflection_questions", [])
    if qs:
        parts.append("📖 **REFLECTION QUESTIONS**\n")
        for q in qs:
            parts.append(f"- {q}")
        parts.append("")
        
    if report_dict.get("uncertainty_note"):
        parts.append(f"*Note: {report_dict['uncertainty_note']}*")
        
    return "\n".join(parts)


@app.route("/api/dream/analyze", methods=["POST"])
def api_analyze_dream():
    data = request.get_json() or {}
    dream_text = (data.get("dream_text") or "").strip()
    if not dream_text:
        return jsonify({"success": False, "message": "Please provide dream text."}), 400

    # Run the pipeline
    result = run_dream_pipeline(dream_text)
    
    # Save the classification result to model.log
    log_model(f"Analyze Input: classification={result.get('classification')} text='{dream_text[:60]}...'")

    # If it is a DREAM and analysis succeeded, store to SQLite history
    if result.get("classification") == "DREAM" and result.get("success"):
        try:
            import sqlite3
            ensure_dir(DATA_DIR)
            conn = sqlite3.connect(os.path.join(DATA_DIR, 'history.db'))
            cur = conn.cursor()
            cur.execute('''CREATE TABLE IF NOT EXISTS history (ts TEXT, dream TEXT, response TEXT)''')
            # For legacy compatibility, save formatted markdown string in response column
            md_report = format_report_as_markdown(result["report"], result["analysis"]["hypotheses"])
            cur.execute('INSERT INTO history (ts,dream,response) VALUES (?,?,?)', (datetime.utcnow().isoformat(), dream_text, md_report))
            conn.commit()
            conn.close()
        except Exception as e:
            print('Failed to save history in api_analyze_dream:', e)

    return jsonify(result)


@app.route("/api/dream/refine", methods=["POST"])
def api_refine_dream():
    data = request.get_json() or {}
    dream_text = (data.get("dream_text") or "").strip()
    original_analysis = data.get("original_analysis") or {}
    feedback_category = (data.get("feedback_category") or "overall").strip()
    feedback_resonance = (data.get("feedback_resonance") or "I am unsure").strip()
    feedback_text = (data.get("feedback_text") or "").strip()

    if not dream_text or not original_analysis:
        return jsonify({"success": False, "message": "Missing dream text or original analysis."}), 400

    result = run_refinement_pipeline(
        dream_text=dream_text,
        original_analysis=original_analysis,
        feedback_category=feedback_category,
        feedback_resonance=feedback_resonance,
        feedback_text=feedback_text
    )
    return jsonify(result)


@app.route("/api/dream/compare", methods=["POST"])
def api_compare_dreams():
    data = request.get_json() or {}
    dreams = data.get("dreams") or []
    if not dreams or len(dreams) < 2:
        return jsonify({"success": False, "message": "Please provide at least 2 dreams to compare."}), 400

    result = run_comparison_pipeline(dreams)
    return jsonify({"success": True, "comparison": result})


@app.route("/interpret", methods=["POST"])
def interpret():
    # Maintain full backwards compatibility for the existing Annotate and Admin pages.
    data = request.get_json() or {}
    dream = (data.get("dream") or "").strip()
    if not dream:
        return jsonify({"success": False, "message": "Please provide a dream text."}), 400

    # Run the new pipeline
    pipeline_res = run_dream_pipeline(dream)
    
    if not pipeline_res.get("success"):
        # Fallback synthesis if pipeline failed
        interpretation_text = synthesize_fallback(dream)
        meta = {"method": "fallback", "error": "Pipeline failed"}
    elif pipeline_res.get("classification") == "NON_DREAM":
        interpretation_text = pipeline_res["message"]
        meta = {"method": "validation", "classification": "NON_DREAM"}
    elif pipeline_res.get("classification") == "AMBIGUOUS":
        interpretation_text = pipeline_res["message"]
        meta = {"method": "validation", "classification": "AMBIGUOUS"}
    else:
        # Structured report formatted as markdown
        interpretation_text = format_report_as_markdown(
            pipeline_res["report"], 
            pipeline_res["analysis"]["hypotheses"]
        )
        meta = {"method": "pipeline", "stages": pipeline_res["processing_stages"]}

    result = {
        "success": True,
        "dream": dream,
        "interpretation": interpretation_text,
        "meta": meta
    }

    # Store to history (sqlite)
    try:
        import sqlite3
        ensure_dir(DATA_DIR)
        conn = sqlite3.connect(os.path.join(DATA_DIR, 'history.db'))
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS history (ts TEXT, dream TEXT, response TEXT)''')
        cur.execute('INSERT INTO history (ts,dream,response) VALUES (?,?,?)', (datetime.utcnow().isoformat(), dream, interpretation_text))
        conn.commit()
        conn.close()
    except Exception as e:
        print('Failed to save history in legacy interpret endpoint:', e)

    return jsonify(result)

@app.route('/history/recent')
def history_recent():
    items = []
    try:
        import sqlite3
        conn = sqlite3.connect(os.path.join(DATA_DIR, 'history.db'))
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
    groq_status = check_groq_health()
    # read last 200 lines of model.log for quick debugging
    log_lines = []
    try:
        with open(os.path.join(LOG_DIR, 'model.log'), 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()
            log_lines = lines[-200:]
    except Exception:
        log_lines = ['No logs yet.']
    return render_template('admin.html', groq=groq_status, logs=log_lines)

@app.route('/admin/reload_models', methods=['POST'])
def admin_reload_models():
    """Check Groq status and report."""
    try:
        status = check_groq_health()
        return jsonify({'success': True, 'status': status})
    except Exception as e:
        log_model(f"admin_reload_models error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/admin/start_worker', methods=['POST'])
def admin_start_worker():
    """Groq is hosted externally; this checks API connectivity."""
    status = check_groq_health()
    return jsonify({'success': True, 'status': status})

@app.route('/contact/submit', methods=['POST'])
def contact_submit():
    payload = request.get_json() or {}
    name = (payload.get('name') or '').strip()
    email = (payload.get('email') or '').strip()
    message = (payload.get('message') or '').strip()
    if not message:
        return jsonify({'success': False, 'message': 'No message provided'}), 400
    ensure_dir(DATA_DIR)
    try:
        with open(os.path.join(DATA_DIR, 'contacts.csv'), 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([datetime.utcnow().isoformat(), name, email, message])
    except Exception as e:
        print('Failed to save contact:', e)
        return jsonify({'success': False, 'message': 'Failed to save contact'}), 500
    return jsonify({'success': True})

@app.route('/_health')
def health_check():
    groq = check_groq_health()
    return jsonify({
        'status': 'ok',
        'groq': groq
    })

@app.route('/_model_status')
def model_status():
    try:
        status = check_groq_health()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/_env_check')
def env_check():
    try:
        # Check for key runtime dependencies without crashing the app
        modules = ['sklearn', 'pandas', 'groq']
        info = {}
        for m in modules:
            try:
                mod = __import__(m)
                ver = getattr(mod, '__version__', 'unknown')
                info[m] = {'installed': True, 'version': str(ver)}
            except Exception as e:
                info[m] = {'installed': False, 'error': str(e)}
        info['python_version'] = sys.version
        info['groq'] = check_groq_health()
        return jsonify(info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    # Print startup info (ASCII-safe for Windows cp1252 consoles)
    print("=" * 60)
    print("  DREAMLENS AI -- Powered by Groq")
    print("=" * 60)

    groq = check_groq_health()
    if groq["connected"]:
        print("  [OK] Groq API connected")
        print(f"  [MODEL] Active: {groq['active_model']}")
        if groq.get("model_available", True):
            print("  [READY] Groq model is ready!")
        else:
            print(f"  [WARN] {groq.get('error')}")
    else:
        print(f"  [ERROR] Groq is unavailable: {groq['error']}")
        print("  [TIP] Set GROQ_API_KEY in your environment")

    print(f"  [DATA] Dream database: {len(dreams_df)} entries loaded")
    print("=" * 60)
    print(f"  [SERVER] Starting on http://127.0.0.1:{port}")
    print("=" * 60)

    # On Windows the Flask reloader can cause socket issues; disable it by default here.
    import platform
    kwargs = dict(host="127.0.0.1", port=port, debug=False, use_reloader=False)
    app.run(**kwargs)
