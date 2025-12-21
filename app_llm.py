"""
DREAMLENS AI - Open Source LLM Integration
Uses Ollama with Mistral/Llama for true AI dream interpretation
"""

import requests
import json
from flask import Flask, render_template, request, jsonify
from pathlib import Path
import csv

app = Flask(__name__)

# ==================== LOAD DATABASE ====================

def load_dream_database():
    """Load dream interpretations from CSV"""
    database = []
    csv_path = Path(__file__).parent / "project" / "cleaned_dream_interpretations.csv"
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                database.append({
                    'word': row.get('Word', '').strip(),
                    'interpretation': row.get('Interpretation', '').strip()
                })
        print(f"Loaded {len(database)} dream interpretations from database")
        return database
    except Exception as e:
        print(f"Error loading database: {e}")
        return []

dreams_database = load_dream_database()

# ==================== OLLAMA LLM INTEGRATION ====================

class OllamaLLMInterpreter:
    """Uses Ollama to run open-source LLM locally"""
    
    def __init__(self, database, model="mistral"):
        self.database = database
        self.model = model
        self.ollama_api = "http://localhost:11434/api/generate"
        self.context = self.build_dream_context()
    
    def build_dream_context(self):
        """Build context for the LLM about dreams"""
        context = """You are an expert dream interpreter with knowledge of:
- Jungian psychology and archetypes
- Freudian analysis of the unconscious
- Modern psychology and emotional processing
- Symbolism and metaphor in dreams
- How dreams reflect waking life

When someone shares a dream with you, provide a comprehensive interpretation that:
1. Identifies and explains major symbols
2. Analyzes emotions and their meaning
3. Discusses psychological themes
4. Connects to potential real-life situations
5. Provides thoughtful reflection questions

Be warm, insightful, and non-judgmental. Focus on self-discovery, not fortune-telling."""
        return context
    
    def search_database(self, dream_text):
        """Search database for related interpretations"""
        if not self.database:
            return []
        
        dream_words = dream_text.lower().split()
        results = []
        
        for entry in self.database:
            entry_word = entry['word'].lower()
            matches = sum(1 for word in dream_words if word in entry_word or entry_word in word)
            
            if matches > 0:
                results.append({
                    'word': entry['word'],
                    'interpretation': entry['interpretation'],
                    'relevance': matches
                })
        
        # Return top 3 results
        results.sort(key=lambda x: x['relevance'], reverse=True)
        return results[:3]
    
    def generate_interpretation(self, dream_text):
        """Use Ollama to generate dream interpretation"""
        
        # Search database for context
        db_results = self.search_database(dream_text)
        db_context = ""
        if db_results:
            db_context = "\n\nRelated dream symbols from our database:\n"
            for result in db_results:
                db_context += f"- {result['word']}: {result['interpretation'][:150]}...\n"
        
        # Create prompt for the LLM
        prompt = f"""{self.context}

Dream shared by user:
"{dream_text}"{db_context}

Please provide a comprehensive, insightful dream interpretation. Structure your response with:

1. INITIAL IMPRESSION
What stands out about this dream and its overall tone?

2. SYMBOL ANALYSIS  
What are the major symbols and what might they represent?

3. EMOTIONAL INTERPRETATION
What emotions are present and what might they reflect?

4. PSYCHOLOGICAL PERSPECTIVE
From Jungian, Freudian, and modern psychology perspectives, what might this dream mean?

5. POTENTIAL MEANINGS
What might this dream be telling the person about their waking life?

6. REFLECTION QUESTIONS
Provide 3-4 thoughtful questions for the dreamer to consider.

Be detailed, warm, and insightful."""

        try:
            # Call Ollama API
            response = requests.post(
                self.ollama_api,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.7,
                    "top_p": 0.9
                },
                timeout=180
            )
            
            if response.status_code == 200:
                result = response.json()
                interpretation = result.get('response', '')
                return interpretation
            else:
                return f"Error: Ollama returned status {response.status_code}"
        
        except requests.exceptions.ConnectionError:
            return """ERROR: Cannot connect to Ollama.

Please ensure:
1. Ollama is installed (https://ollama.ai)
2. Ollama is running (ollama serve)
3. A model is downloaded (ollama pull mistral)

Once Ollama is running, refresh this page and try again."""
        
        except requests.exceptions.Timeout:
            return "ERROR: Ollama response timed out. The model might be processing. Please try again."
        
        except Exception as e:
            return f"ERROR: {str(e)}"


# Initialize interpreter
interpreter = OllamaLLMInterpreter(dreams_database, model="mistral")

# ==================== FLASK ROUTES ====================

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat")
def chat():
    return render_template("chat.html")

@app.route("/interpret", methods=["POST"])
def interpret():
    """Main endpoint for dream interpretation using Ollama"""
    try:
        data = request.get_json()
        user_dream = data.get("dream", "").strip()
        
        if not user_dream or len(user_dream.split()) < 2:
            return jsonify({
                "success": False,
                "message": "Please describe your dream. Even a short description helps!"
            })
        
        # Generate interpretation using Ollama
        result = interpreter.generate_interpretation(user_dream)
        
        # Check if it's an error
        if result.startswith("ERROR"):
            return jsonify({
                "success": False,
                "message": result
            })
        
        return jsonify({
            "success": True,
            "interpretation": result
        })
    
    except Exception as e:
        print(f"Error in interpret endpoint: {e}")
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        })

@app.route("/health")
def health():
    """Check system status"""
    # Try to connect to Ollama
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        ollama_status = "Connected" if response.status_code == 200 else "Disconnected"
    except:
        ollama_status = "Disconnected"
    
    return jsonify({
        "status": "OK",
        "message": "DreamLens AI - Open Source LLM Edition",
        "database_size": len(dreams_database),
        "ollama_status": ollama_status,
        "model": interpreter.model
    })

if __name__ == "__main__":
    import os
    print("=" * 70)
    print("DREAMLENS AI - OPEN SOURCE LLM EDITION")
    print("=" * 70)
    print(f"Dream Database: {len(dreams_database)} interpretations loaded")
    print(f"LLM Backend: Ollama with {interpreter.model} model")
    print("=" * 70)
    
    # Get configuration from environment
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    port = int(os.getenv("PORT", 5000))
    
    app.run(debug=debug_mode, host="0.0.0.0", port=port)
