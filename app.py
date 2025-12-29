from flask import Flask, render_template, request, jsonify
import pandas as pd
import random

app = Flask(__name__)

# Load your dataset
try:
    dreams_df = pd.read_csv("cleaned_dream_interpretations.csv")
    if "Word" not in dreams_df.columns or "Interpretation" not in dreams_df.columns:
        raise ValueError("CSV file must contain 'Word' and 'Interpretation' columns.")
except Exception as e:
    print(f"Error loading dataset: {e}")
    dreams_df = pd.DataFrame(columns=["Word", "Interpretation"])

# Fallback AI-style interpretations
fallback_responses = [
    "Dreams about {topic} can reflect a desire for transformation or escape from daily stress. It might be your mind signaling the need for change.",
    "When you dream of {topic}, it often symbolizes emotional shifts or inner awakening. Consider what’s been changing in your life recently.",
    "This dream suggests that your subconscious is processing a deep thought or event. Pay attention to your emotions connected with {topic}.",
    "It could represent your journey through unknown territories in life. Embrace it with courage — something beautiful might be ahead.",
    "This may point toward unresolved thoughts or future possibilities. It’s your mind’s way of helping you grow stronger mentally."
]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/interpret", methods=["POST"])
def interpret():
    data = request.get_json()
    user_dream = data.get("dream", "").strip().lower()

    if not user_dream:
        return jsonify({"response": "Please enter a dream to interpret."})

    # Step 1: Try exact keyword matching
    best_match = None
    best_interpretation = None

    for _, row in dreams_df.iterrows():
        word = str(row["Word"]).lower()
        interpretation = row["Interpretation"]
        
        # Check if the keyword (word) is in the user dream
        if word in user_dream:
            best_match = word
            best_interpretation = interpretation
            break  # Exit once a match is found

    # Step 2: Return the match or AI fallback
    if best_match:
        return jsonify({"response": f"✨ Interpretation:\n{best_interpretation}"})

    # Step 3: AI-style fallback
    topic = user_dream.split()[0] if user_dream else "your dream"
    ai_response = random.choice(fallback_responses).format(topic=topic)
    
    return jsonify({"response": f"🤖 AI Insight:\n{ai_response}"})


if __name__ == "__main__":
    app.run(debug=True)
