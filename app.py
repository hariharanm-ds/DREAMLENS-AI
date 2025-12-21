from flask import Flask, render_template, request, jsonify
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from nltk.corpus import wordnet
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# Load dataset for structured dream interpretations
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

# Load gpt2-medium model and tokenizer
def load_gpt2():
    try:
        tokenizer = AutoTokenizer.from_pretrained("gpt2-medium")
        model = AutoModelForCausalLM.from_pretrained("gpt2-medium")
        return tokenizer, model
    except Exception as e:
        print(f"Error loading GPT-2 Medium model: {e}")
        return None, None

tokenizer, model = load_gpt2()

# Initialize TF-IDF for semantic word matching
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(dreams_df["Word"])

def find_related_word(user_dream):
    """Find synonyms using WordNet to improve keyword matching."""
    words = user_dream.split()
    for word in words:
        synsets = wordnet.synsets(word)
        if synsets:
            return synsets[0].lemmas()[0].name()  # Get closest synonym
    return user_dream  # If no match, return original

def find_best_match(user_dream):
    """Search dataset for closest dream interpretation using TF-IDF similarity."""
    user_vector = vectorizer.transform([user_dream])
    similarities = cosine_similarity(user_vector, tfidf_matrix).flatten()
    best_match_index = similarities.argmax()
    best_match_score = similarities[best_match_index]
    if best_match_score > 0.3:
        return dreams_df.iloc[best_match_index]["Interpretation"]
    return None

def generate_gpt2_response(user_dream):
    """Generate a detailed AI-based dream interpretation using GPT-2."""
    few_shot_prompt = (
        "Someone dreamed of being chased by a giant snake. This dream may symbolize hidden fears, anxiety, or a threat that the person is avoiding.\n"
        "Someone dreamed of flying freely over mountains. This dream may symbolize a desire for freedom, ambition, or rising above current challenges.\n"
        "Someone dreamed of hugging their childhood dog. This dream may symbolize longing, comfort, or emotional healing.\n"
        f"Someone dreamed of {user_dream}. This dream may symbolize"
    )
    
    try:
        inputs = tokenizer.encode(few_shot_prompt, return_tensors="pt")
        outputs = model.generate(
            inputs,
            max_length=inputs.shape[1] + 150,  # Increase max_length for more detailed responses
            num_return_sequences=1,
            no_repeat_ngram_size=2,
            temperature=0.8,
            top_p=0.95,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
        decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract only the last line (the new interpretation)
        last_line = decoded.strip().split('\n')[-1]
        interpretation = last_line.replace(f"Someone dreamed of {user_dream}. This dream may symbolize", "").strip()
        
        # Post-process the interpretation to add more details
        refined_response = interpretation + " This interpretation could represent your current emotional state, unresolved feelings, or desires you may not be fully aware of."
        
        return f"This dream may symbolize {refined_response}"
    except Exception as e:
        print(f"Error in GPT-2 generation: {e}")
        return "Sorry, I couldn't generate a proper interpretation."

def interpret_dream(user_dream):
    """Main logic for interpreting a user's dream."""
    user_dream = user_dream.strip().lower()
    if not user_dream:
        return "Please enter a dream to interpret."

    # Step 1: Try structured dataset
    refined_dream = find_related_word(user_dream)
    structured_interpretation = find_best_match(refined_dream)
    if structured_interpretation:
        return f"✨ Interpretation:\n{structured_interpretation}"

    # Step 2: GPT-2 generation
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
