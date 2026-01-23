from flask import Flask, render_template, request, jsonify
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from nltk.corpus import wordnet
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

def load_data():
    try:
        dreams_df = pd.read_csv("project/cleaned_dream_interpretations.csv")
        if "Word" not in dreams_df.columns or "Interpretation" not in dreams_df.columns:
            raise ValueError("CSV must contain 'Word' and 'Interpretation' columns.")
        return dreams_df
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return pd.DataFrame(columns=["Word", "Interpretation"])

dreams_df = load_data()

def load_gpt2():
    try:
        tokenizer = AutoTokenizer.from_pretrained("gpt2-medium")
        model = AutoModelForCausalLM.from_pretrained("gpt2-medium")
        return tokenizer, model
    except Exception as e:
        print(f"Error loading GPT-2 Medium model: {e}")
        return None, None

tokenizer, model = load_gpt2()

vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(dreams_df["Word"])

def find_related_word(user_dream):
    words = user_dream.split()
    for word in words:
        synsets = wordnet.synsets(word)
        if synsets:
            return synsets[0].lemmas()[0].name() 
    return user_dream  

def find_best_match(user_dream):
    user_vector = vectorizer.transform([user_dream])
    similarities = cosine_similarity(user_vector, tfidf_matrix).flatten()
    best_match_index = similarities.argmax()
    best_match_score = similarities[best_match_index]
    if best_match_score > 0.3:
        return dreams_df.iloc[best_match_index]["Interpretation"]
    return None

def generate_gpt2_response(user_dream):
    few_shot_prompt = (
        "Dream: Being chased by a giant snake\n"
        "Interpretation: This dream may symbolize hidden fears, anxiety, or a threat the person is avoiding.\n"
        "Dream: Flying freely over mountains\n"
        "Interpretation: This dream may symbolize a desire for freedom, ambition, or rising above challenges.\n"
        "Dream: Hugging a childhood dog\n"
        "Interpretation: This dream may symbolize longing, comfort, or emotional healing.\n"
        f"Dream: {user_dream}\n"
        "Interpretation:"
    )

    try:
        inputs = tokenizer.encode(few_shot_prompt, return_tensors="pt")
        attention_mask = torch.ones(inputs.shape, device=inputs.device)
        
        outputs = model.generate(
            inputs,
            max_length=inputs.shape[1] + 150,
            num_return_sequences=1,
            no_repeat_ngram_size=2,
            temperature=0.8,
            top_p=0.95,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
            attention_mask=attention_mask
        )
        
        decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)

        interpretation = decoded.split("Interpretation:")[-1].strip()

        refined_response = interpretation

        return f"This dream may symbolize {refined_response}"
    except Exception as e:
        print(f"Error in GPT-2 generation: {e}")
        return "Sorry, I couldn't generate a proper interpretation."


def interpret_dream(user_dream):
    user_dream = user_dream.strip().lower()
    if not user_dream or len(user_dream.split()) < 3:
        return "Please enter a complete dream description with a few more words."

    meaningful_words = [word for word in user_dream.split() if wordnet.synsets(word)]
    if len(meaningful_words) == 0:
        return "Sorry, I couldn't recognize any meaningful words. Please describe your dream more clearly."

    refined_dream = find_related_word(user_dream)
    structured_interpretation = find_best_match(refined_dream)
    if structured_interpretation:
        return f"✨ Interpretation:\n{structured_interpretation}"

    gpt2_prompt = f"Someone dreamed of {user_dream}. What could this dream mean in psychological or emotional terms?"
    ai_response = generate_gpt2_response(gpt2_prompt)
    return f"🤖 AI Insight:\n{ai_response}"


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat")
def chat():
    return render_template("chat.html")

@app.route("/interpret", methods=["POST"])
def interpret():
    data = request.get_json()
    user_dream = data.get("dream", "").strip()
    response = interpret_dream(user_dream)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)
