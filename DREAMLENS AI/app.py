from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
import random
from functools import lru_cache

# NLP & ML libraries (models are lazy-loaded)
# Avoid importing heavy transformer modules at top-level to speed service startup.
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

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

# ---------- Zero-shot classifier and generator (free models) ----------
# Using 'facebook/bart-large-mnli' for zero-shot and 'google/flan-t5-small' for generation

@lru_cache(maxsize=1)
def get_zsc_pipeline():
    try:
        from transformers import pipeline as hf_pipeline
        print("Loading zero-shot classification model...")
        return hf_pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    except Exception as e:
        print("Failed to load zero-shot model:", e)
        return None

@lru_cache(maxsize=1)
def get_flan_models():
    try:
        print("Loading Flan-T5 generation model...")
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small")
        model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small")
        return tokenizer, model
    except Exception as e:
        print("Failed to load Flan-T5 model:", e)
        return None, None

# Predefined label candidates for zero-shot classification (can be extended)
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


def generate_interpretation_with_flan(dream_text: str, labels: list[str]):
    """Generate a human-readable interpretation using Flan-T5 prompt."""
    tokenizer, model = get_flan_models()
    if tokenizer is None or model is None:
        # Fallback to a template-based explanation
        label_text = ", ".join(labels[:5]) if labels else "general emotions"
        return f"This dream seems related to {label_text}. It may reflect your current emotional state, unresolved feelings, or recent experiences. Try journaling about who, what, and where in your dream to gain clarity."

    prompt = (
        f"Interpret this dream in psychological terms and provide 2 short suggestions for reflection or coping:\n\n" 
        f"Dream: \"{dream_text}\"\n" 
        f"Key indicators: {', '.join(labels)}\n\n" 
        f"Response format:\n- Interpretation:\n- Suggestions:\n"
    )

    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_length=200, do_sample=True, top_p=0.9, temperature=0.7)
    decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return decoded.strip()

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

    # 1) Try dataset match
    structured = find_best_match_simple(dream.lower())

    # 2) Zero-shot labels
    labels = []
    try:
        zsc = get_zsc_pipeline()
        if zsc is not None:
            zsc_res = zsc(dream, LABEL_CANDIDATES, multi_label=True)
            labels = [lab for lab, score in zip(zsc_res['labels'], zsc_res['scores']) if score > 0.20][:6]
    except Exception as e:
        print("Zero-shot classification error:", e)

    # 3) Generate explanation
    interpretation_text = ""
    if structured:
        interpretation_text = structured['interpretation']
        meta = {"method": "dataset", "score": structured['score']}
    else:
        # Ensure flan models are loaded lazily
        tokenizer, model = get_flan_models()
        interpretation_text = generate_interpretation_with_flan(dream, labels)
        meta = {"method": "flan-t5", "labels": labels, "gen_loaded": bool(tokenizer and model)}

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


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

