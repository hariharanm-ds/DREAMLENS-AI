from flask import Flask, render_template, request, jsonify
import csv
import json
import os
from difflib import SequenceMatcher
from collections import Counter
import re

app = Flask(__name__)

# ==================== LOAD DREAM DATASET ====================
def load_data():
    """Load dream interpretation dataset from CSV"""
    dreams_data = {}
    try:
        with open("project/cleaned_dream_interpretations.csv", 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'Word' in row and 'Interpretation' in row:
                    word_key = row['Word'].lower().strip()
                    dreams_data[word_key] = {
                        'word': row['Word'],
                        'interpretation': row['Interpretation']
                    }
    except Exception as e:
        print(f"Error loading dataset: {e}")
    
    return dreams_data

dreams_database = load_data()
print(f"Loaded {len(dreams_database)} dream symbols")

# ==================== DREAM INTERPRETATION FRAMEWORK ====================

# Common dream symbols with interpretations
DREAM_SYMBOLS = {
    'water': {
        'keywords': ['water', 'ocean', 'sea', 'river', 'lake', 'rain', 'flood', 'swimming', 'drowning'],
        'interpretation': 'Water represents emotions, the subconscious mind, and your emotional state. Calm water suggests peace and tranquility. Turbulent or murky water indicates emotional disturbance, uncertainty, or unresolved feelings. Drowning suggests feeling overwhelmed by emotions.'
    },
    'flying': {
        'keywords': ['flying', 'soaring', 'air', 'sky', 'hover', 'gliding', 'levitate'],
        'interpretation': 'Flying symbolizes freedom, perspective, ambition, and liberation from constraints. It may indicate a desire to escape from current situations or rise above challenges. Difficulty flying suggests obstacles or self-doubt. Effortless flight represents confidence and control.'
    },
    'chase': {
        'keywords': ['chase', 'chased', 'running', 'escape', 'pursued', 'hunted', 'flee'],
        'interpretation': 'Being chased represents anxiety, avoidance, or unresolved conflict. It suggests something in your waking life that you\'re running from or avoiding. This could be a fear, responsibility, or difficult emotion that needs confronting.'
    },
    'death': {
        'keywords': ['death', 'dying', 'dead', 'killing', 'killed', 'funeral', 'grave'],
        'interpretation': 'Death in dreams rarely means literal death. It usually symbolizes transformation, endings, transitions, or new beginnings. It may represent letting go of old patterns, relationships, or beliefs. Consider what aspect of yourself or your life is changing.'
    },
    'fall': {
        'keywords': ['fall', 'falling', 'drop', 'collapse', 'tumble', 'plunge'],
        'interpretation': 'Falling represents loss of control, anxiety, fear of failure, or feeling overwhelmed. It may indicate insecurity, vulnerability, or lack of support. The feeling upon waking is important - shock vs. peaceful descent changes the meaning.'
    },
    'house': {
        'keywords': ['house', 'home', 'building', 'room', 'basement', 'attic', 'door', 'window'],
        'interpretation': 'A house represents yourself and your mind. Different rooms symbolize different aspects of your personality or life areas. The attic may represent higher thoughts, basement represents the unconscious, and each room can relate to specific emotions or memories.'
    },
    'snake': {
        'keywords': ['snake', 'serpent', 'reptile', 'cobra', 'venom', 'scales'],
        'interpretation': 'Snakes can represent fear, threat, or hidden danger. But they also symbolize transformation, healing, wisdom, and renewal (due to shedding skin). The context is crucial - a coiled snake ready to strike differs from a peaceful snake shedding its skin.'
    },
    'animal': {
        'keywords': ['dog', 'cat', 'bird', 'horse', 'lion', 'tiger', 'bear', 'wolf'],
        'interpretation': 'Animals represent instincts, behaviors, or aspects of yourself. Aggressive animals may indicate suppressed anger or fear. Gentle animals suggest comfort, loyalty, or positive instincts. Consider the animal\'s natural characteristics and your emotional response to it.'
    },
    'family': {
        'keywords': ['mother', 'father', 'parent', 'sister', 'brother', 'son', 'daughter', 'family', 'relative'],
        'interpretation': 'Family members usually represent aspects of yourself or your relationships with them. Parents may symbolize authority, protection, or guidance. Siblings might represent different facets of your personality or your actual relationship with them.'
    },
    'vehicle': {
        'keywords': ['car', 'truck', 'plane', 'train', 'bus', 'bicycle', 'motorcycle', 'boat'],
        'interpretation': 'Vehicles represent the journey of life and your direction. The condition and control of the vehicle indicate how you feel about your life path. A broken-down car suggests feeling stuck, while driving smoothly indicates good progress and control.'
    }
}

# Emotional keywords
EMOTIONAL_KEYWORDS = {
    'positive': ['happy', 'joy', 'love', 'beautiful', 'peaceful', 'calm', 'comfortable', 'safe', 'success', 'victory'],
    'negative': ['fear', 'scared', 'anxious', 'worried', 'afraid', 'danger', 'threat', 'pain', 'sad', 'upset'],
    'neutral': ['strange', 'weird', 'odd', 'confusing', 'unusual', 'curious', 'interested']
}

# ==================== HELPER FUNCTIONS ====================

def string_similarity(a, b):
    """Calculate similarity between two strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def extract_dream_symbols(dream_text):
    """Extract dream symbols from user's dream"""
    dream_lower = dream_text.lower()
    found_symbols = []
    
    for symbol, details in DREAM_SYMBOLS.items():
        for keyword in details['keywords']:
            if keyword in dream_lower:
                found_symbols.append({
                    'symbol': symbol,
                    'keyword': keyword,
                    'interpretation': details['interpretation']
                })
                break  # Only add once per symbol
    
    return found_symbols

def extract_emotional_context(dream_text):
    """Detect emotional context from dream"""
    dream_lower = dream_text.lower()
    emotions = {'positive': 0, 'negative': 0, 'neutral': 0}
    
    for emotion_type, keywords in EMOTIONAL_KEYWORDS.items():
        for keyword in keywords:
            if keyword in dream_lower:
                emotions[emotion_type] += 1
    
    return emotions

# Psychological frameworks and common interpretations
PSYCHOLOGICAL_INTERPRETATIONS = {
    'action': {
        'running': 'suggests urgency, escape, or avoidance of something in your waking life',
        'walking': 'represents your life journey and current direction or progress',
        'jumping': 'indicates ambition, overcoming obstacles, or taking big steps in life',
        'climbing': 'symbolizes striving for goals, overcoming challenges, or reaching for success',
        'falling': 'represents loss of control, anxiety, insecurity, or fear of failure',
        'fighting': 'indicates conflict, struggle with inner demons, or confrontation needed',
        'dancing': 'expresses freedom, joy, celebration, or harmony in your life',
        'hiding': 'suggests avoidance, shame, secrets, or fear of being discovered',
        'searching': 'represents looking for something missing in your life or answers',
        'finding': 'indicates discovery, success, resolution, or gaining new perspective',
    },
    'emotion': {
        'fear': 'indicates anxiety, worry, or something threatening in waking life needs addressing',
        'happy': 'suggests positive developments, contentment, or alignment with your desires',
        'sad': 'represents grief, loss, disappointment, or unresolved emotional pain',
        'angry': 'indicates frustration, resentment, or suppressed anger that needs release',
        'confused': 'suggests uncertainty, lack of clarity, or need for direction in decisions',
        'excited': 'indicates enthusiasm, anticipation, or positive energy about future events',
        'anxious': 'represents worry, stress, or fear about something in your waking life',
        'peaceful': 'suggests harmony, acceptance, or resolution of previous conflicts',
    },
    'setting': {
        'house': 'represents yourself and your mind; different rooms are different life aspects',
        'school': 'indicates learning, growth, or revisiting old lessons and patterns',
        'work': 'reflects career concerns, productivity, stress, or achievement goals',
        'forest': 'suggests being lost, confusion, or navigating complex situations',
        'mountain': 'represents challenges to overcome, high goals, or reaching new heights',
        'ocean': 'indicates vastness of possibilities, emotions, or the unconscious mind',
        'city': 'suggests complex social interactions, progress, or feeling overwhelmed',
        'dark': 'represents unknown aspects of self, fear, or the unconscious mind',
        'light': 'indicates clarity, hope, consciousness, or positive enlightenment',
    },
    'person': {
        'stranger': 'may represent unknown aspect of yourself or unfamiliar situation',
        'family': 'reflects your actual relationships or different facets of your personality',
        'friend': 'indicates support, aspects of that person you admire, or your own qualities',
        'enemy': 'represents inner conflict, actual conflict, or shadow self aspects',
        'celebrity': 'suggests qualities you admire, aspire to, or project onto yourself',
        'child': 'represents innocence, potential, vulnerability, or your inner child',
        'authority': 'indicates your relationship with power, rules, or parental figures',
    },
    'object': {
        'key': 'represents unlocking potential, solving mysteries, or access to new opportunities',
        'door': 'indicates new opportunities, transitions, or unexplored aspects of self',
        'mirror': 'suggests self-reflection, facing truth about yourself, or self-awareness',
        'weapon': 'indicates conflict, aggression, defense mechanisms, or inner power',
        'money': 'represents value, power, worth, security, or resource allocation',
        'car': 'suggests your journey, direction, control, or current life momentum',
        'phone': 'indicates communication, connection, or message from unconscious',
        'book': 'represents knowledge, learning, stories, or messages waiting to be understood',
    }
}

def generate_smart_interpretation(dream_text):
    """Generate intelligent interpretation based on dream content"""
    dream_lower = dream_text.lower()
    
    interpretations = []
    found_concepts = False
    
    # Check for psychological keywords in dream
    for category, keywords_dict in PSYCHOLOGICAL_INTERPRETATIONS.items():
        for keyword, interpretation in keywords_dict.items():
            if keyword in dream_lower:
                interpretations.append(f"* The {keyword} in your dream {interpretation}")
                found_concepts = True
    
    if not found_concepts:
        # Generate generic but meaningful interpretation
        interpretations.append("* Your dream presents themes that are worth exploring.")
        interpretations.append("* The subconscious often uses symbolic language to communicate.")
        interpretations.append("* Consider what emotions and sensations stood out most.")
    
    return interpretations

def analyze_dream_depth(dream_text):
    """Provide deeper analysis of dream elements"""
    dream_lower = dream_text.lower()
    analysis = []
    
    # Check for common dream themes
    themes = {
        'death/transformation': ['death', 'dying', 'dead', 'killed', 'funeral', 'grave', 'transform'],
        'change/growth': ['change', 'evolve', 'grow', 'develop', 'shift', 'progress'],
        'relationships': ['love', 'relationship', 'friend', 'family', 'partner', 'meeting', 'social'],
        'work/achievement': ['work', 'job', 'success', 'fail', 'win', 'lose', 'accomplish', 'career'],
        'movement/journey': ['travel', 'journey', 'walk', 'run', 'move', 'drive', 'fly', 'path'],
        'conflict/struggle': ['fight', 'battle', 'conflict', 'struggle', 'enemy', 'danger', 'attack'],
        'mystery/uncertainty': ['unknown', 'mystery', 'strange', 'weird', 'confusing', 'lost', 'unclear'],
    }
    
    for theme, keywords in themes.items():
        for keyword in keywords:
            if keyword in dream_lower:
                analysis.append(theme)
                break
    
    return analysis

def get_symbolic_meaning(dream_text):
    """Extract and provide symbolic meanings"""
    meanings = []
    dream_lower = dream_text.lower()
    
    # Color symbolism
    if 'red' in dream_lower:
        meanings.append("Red often symbolizes passion, anger, danger, or strong emotions")
    if 'blue' in dream_lower:
        meanings.append("Blue typically represents calm, sadness, truth, or communication")
    if 'green' in dream_lower:
        meanings.append("Green symbolizes growth, healing, nature, or renewal")
    if 'black' in dream_lower:
        meanings.append("Black often represents the unknown, death, mystery, or the unconscious")
    if 'white' in dream_lower:
        meanings.append("White typically symbolizes purity, clarity, new beginnings, or goodness")
    if 'gold' in dream_lower or 'yellow' in dream_lower:
        meanings.append("Gold/Yellow represent illumination, positivity, wealth, or enlightenment")
    
    # Number symbolism
    if '3' in dream_lower or 'three' in dream_lower:
        meanings.append("Three represents completeness, balance, or wholeness")
    if '7' in dream_lower or 'seven' in dream_lower:
        meanings.append("Seven symbolizes spiritual awakening, mystery, or perfection")
    if '13' in dream_lower:
        meanings.append("Thirteen often relates to transformation or completion of cycles")
    
    return meanings

def search_database(dream_text):
    """Search dream database for matching interpretations with flexible matching"""
    results = []
    dream_words = dream_text.lower().split()
    
    # First pass: exact and partial word matches
    for db_key, db_entry in dreams_database.items():
        similarity = 0
        
        # Check for direct word match
        if db_key in dream_text.lower():
            similarity = 1.0
        else:
            # Check for partial matches in words
            for dream_word in dream_words:
                word_similarity = string_similarity(dream_word, db_key)
                similarity = max(similarity, word_similarity)
        
        if similarity > 0.35:  # Lower threshold for more matches
            results.append({
                'word': db_entry['word'],
                'interpretation': db_entry['interpretation'],
                'score': similarity
            })
    
    # Sort by similarity score
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:5]  # Return top 5 matches

def generate_interpretation(dream_text):
    """Generate friendly, comprehensive dream interpretation"""
    # Extract symbols
    symbols = extract_dream_symbols(dream_text)
    
    # Extract emotions
    emotions = extract_emotional_context(dream_text)
    
    # Search database
    db_results = search_database(dream_text)
    
    # Generate smart interpretations
    smart_interpretations = generate_smart_interpretation(dream_text)
    
    # Analyze depth
    themes = analyze_dream_depth(dream_text)
    
    # Get symbolic meanings
    symbolic_meanings = get_symbolic_meaning(dream_text)
    
    # Build friendly interpretation
    interpretation = []
    
    interpretation.append("DREAM ANALYSIS\n")
    interpretation.append("=" * 50 + "\n\n")
    
    # Add symbol-based interpretation (friendly)
    if symbols:
        interpretation.append("WHAT YOU SAW:\n")
        for sym in symbols[:3]:
            interpretation.append(f"\n* {sym['symbol'].title()}\n")
            interpretation.append(f"  {sym['interpretation']}\n")
        interpretation.append("\n")
    
    # Add theme analysis (friendly)
    if themes:
        interpretation.append("WHAT IT'S ABOUT:\n")
        interpretation.append("Your dream is exploring themes of:\n")
        for theme in themes:
            interpretation.append(f"* {theme}\n")
        interpretation.append("\n")
    
    # Add smart interpretation (friendly)
    if smart_interpretations:
        interpretation.append("KEY MEANINGS:\n")
        for smart_int in smart_interpretations[:4]:
            interpretation.append(f"{smart_int}\n")
        interpretation.append("\n")
    
    # Add symbolic meanings if found (friendly)
    if symbolic_meanings:
        interpretation.append("SYMBOLIC COLORS & NUMBERS:\n")
        for meaning in symbolic_meanings:
            interpretation.append(f"* {meaning}\n")
        interpretation.append("\n")
    
    # Add database matches (friendly)
    if db_results:
        interpretation.append("RELATED DREAM INSIGHTS:\n")
        for i, result in enumerate(db_results[:2], 1):
            # Truncate long interpretations
            text = result['interpretation']
            if len(text) > 150:
                text = text[:150] + "..."
            interpretation.append(f"\n{i}. {result['word']}: {text}\n")
        interpretation.append("\n")
    
    # Add emotional context (friendly)
    interpretation.append("HOW YOU FELT:\n")
    if emotions['positive'] > emotions['negative']:
        interpretation.append("Your dream has a positive, hopeful energy. You may be experiencing growth or moving toward something good in your life.\n\n")
    elif emotions['negative'] > emotions['positive']:
        interpretation.append("Your dream carries some worry or concern. This is your mind's way of helping you process challenges. Pay attention to what felt difficult.\n\n")
    else:
        interpretation.append("Your dream presents a mix of emotions, showing you're processing different aspects of your life.\n\n")
    
    # Add psychological insight (friendly)
    interpretation.append("WHAT YOUR MIND IS TELLING YOU:\n")
    interpretation.append("Dreams are your mind's creative way of working through feelings, memories, and experiences. ")
    interpretation.append("The symbols and themes in YOUR dream are uniquely personal to you - they're messages from your subconscious.\n\n")
    
    # Add reflection prompt (friendly)
    interpretation.append("REFLECT ON THESE QUESTIONS:\n")
    interpretation.append("* What feelings or situations in your life match what happened in the dream?\n")
    interpretation.append("* Is there something you've been avoiding or need to address?\n")
    interpretation.append("* What changes or growth might this dream be suggesting?\n")
    interpretation.append("* How can you use these insights in your waking life?\n")
    
    return ''.join(interpretation)



# ==================== FLASK ROUTES ====================

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat")
def chat():
    return render_template("chat.html")

@app.route("/interpret", methods=["POST"])
def interpret():
    """Main endpoint for dream interpretation"""
    try:
        data = request.get_json()
        user_dream = data.get("dream", "").strip()
        
        if not user_dream:
            return jsonify({"success": False, "message": "Please enter a dream description."})
        
        result = generate_interpretation(user_dream)
        return jsonify({"success": True, "interpretation": result})
    
    except Exception as e:
        print(f"Error in interpret endpoint: {e}")
        return jsonify({"success": False, "message": "An error occurred. Please try again."})

@app.route("/health")
def health():
    return jsonify({
        "status": "OK", 
        "message": "Dream interpretation service is running",
        "symbols_available": len(DREAM_SYMBOLS),
        "dreams_in_database": len(dreams_database)
    })

if __name__ == "__main__":
    print("Starting DreamLens AI Server...")
    print(f"Dream Database: {len(dreams_database)} interpretations loaded")
    print(f"Dream Symbols: {len(DREAM_SYMBOLS)} symbol patterns available")
    app.run(debug=True)
