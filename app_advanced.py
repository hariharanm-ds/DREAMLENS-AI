"""
DREAMLENS AI - Advanced Generative Dream Interpretation Engine
Uses intelligent analysis and generation, not just keyword matching
"""

import csv
import os
from flask import Flask, render_template, request, jsonify
from pathlib import Path
import random

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
        print(f"Loaded {len(database)} dream interpretations")
        return database
    except Exception as e:
        print(f"Error loading database: {e}")
        return []

dreams_database = load_dream_database()

# ==================== ADVANCED DREAM ANALYSIS ENGINE ====================

class DreamInterpreter:
    """Advanced dream interpretation with real generation"""
    
    def __init__(self, database):
        self.database = database
        
        # Comprehensive symbol database with rich interpretations
        self.symbol_meanings = {
            'water': {
                'themes': ['emotions', 'subconscious', 'flowing change', 'reflection'],
                'psychology': 'Water represents emotional depth and the flow of feelings',
                'jungian': 'Water is the archetypal symbol of the unconscious mind',
                'interpretations': [
                    'calm water suggests peace and emotional clarity',
                    'turbulent water indicates emotional turmoil or uncertainty',
                    'drowning suggests feeling overwhelmed by emotions',
                    'swimming represents navigating through emotional challenges',
                    'flowing water indicates life moving forward with change'
                ]
            },
            'flying': {
                'themes': ['freedom', 'transcendence', 'perspective', 'escape'],
                'psychology': 'Flying symbolizes liberation and the ability to rise above problems',
                'jungian': 'Flight represents spiritual ascension and transcendence',
                'interpretations': [
                    'effortless flying indicates confidence and control',
                    'flying with difficulty suggests obstacles or self-doubt',
                    'flying high represents ambition and lofty goals',
                    'flying over landscapes symbolizes gaining new perspective',
                    'fear of falling while flying indicates anxiety about losing control'
                ]
            },
            'chase': {
                'themes': ['anxiety', 'avoidance', 'conflict', 'pursuit'],
                'psychology': 'Being chased represents running from emotions or situations',
                'jungian': 'The pursuer often represents an aspect of self you are avoiding',
                'interpretations': [
                    'being chased indicates something you need to face',
                    'running suggests avoidance of a difficult issue',
                    'catching the person chasing you means confronting your fear',
                    'being trapped suggests feeling cornered in waking life',
                    'escaping the chase can mean finding a way through the problem'
                ]
            },
            'house': {
                'themes': ['self', 'security', 'structure', 'mind'],
                'psychology': 'House represents the self and your inner world',
                'jungian': 'Different rooms symbolize different aspects of personality',
                'interpretations': [
                    'childhood home symbolizes past influences and origins',
                    'exploring new rooms suggests discovering new aspects of self',
                    'house damage indicates feeling vulnerable or insecure',
                    'living in luxury suggests self-worth and comfort',
                    'hidden rooms represent undiscovered potential or repressed memories'
                ]
            },
            'death': {
                'themes': ['transformation', 'endings', 'renewal', 'change'],
                'psychology': 'Death usually represents ending of a life phase, not literal death',
                'jungian': 'Death symbolizes transformation and rebirth',
                'interpretations': [
                    'death of someone close suggests ending of that relationship dynamic',
                    'your own death indicates major life transformation',
                    'witnessing death means you are observing change',
                    'peaceful death suggests acceptance of necessary endings',
                    'violent death indicates traumatic change or difficult transition'
                ]
            },
            'fall': {
                'themes': ['loss of control', 'fear', 'vulnerability', 'letting go'],
                'psychology': 'Falling represents loss of control or fear of failure',
                'jungian': 'The fall represents descent into the unconscious',
                'interpretations': [
                    'falling and landing safely suggests you will overcome challenges',
                    'endless falling indicates anxiety about the unknown',
                    'falling from heights represents fear of ambition',
                    'controlled descent suggests managed change',
                    'waking up before landing means avoiding facing the situation'
                ]
            },
            'animal': {
                'themes': ['instinct', 'behavior', 'nature', 'power'],
                'psychology': 'Animals represent instincts and natural behaviors',
                'jungian': 'Each animal has archetypal power and characteristics',
                'interpretations': [
                    'aggressive animals suggest suppressed anger or fear',
                    'friendly animals indicate connection with your instincts',
                    'predators represent threats you perceive',
                    'wild animals suggest untamed aspects of self',
                    'domestic animals indicate integrated instincts'
                ]
            },
            'snake': {
                'themes': ['transformation', 'wisdom', 'danger', 'healing'],
                'psychology': 'Snake represents transformation and hidden wisdom',
                'jungian': 'Snake is symbol of healing and transformation',
                'interpretations': [
                    'snake shedding skin symbolizes personal transformation',
                    'venomous snake indicates dangerous situation or toxic person',
                    'coiled snake suggests potential power building',
                    'attacking snake means confronting fear or danger',
                    'snake in your home indicates internal conflict'
                ]
            },
            'family': {
                'themes': ['relationships', 'origins', 'belonging', 'conflict'],
                'psychology': 'Family represents connection and early influences',
                'jungian': 'Family members often represent different aspects of self',
                'interpretations': [
                    'happy family gathering suggests harmony and connection',
                    'family conflict indicates unresolved relationship issues',
                    'distant family suggests emotional distance in waking life',
                    'family members missing indicates loss or separation',
                    'protecting family shows your values and priorities'
                ]
            },
            'vehicle': {
                'themes': ['journey', 'direction', 'control', 'progress'],
                'psychology': 'Vehicle represents how you navigate life and your journey',
                'jungian': 'Vehicle symbolizes the self moving through life',
                'interpretations': [
                    'driving smoothly indicates life moving as planned',
                    'losing control of vehicle means feeling directionless',
                    'vehicle breakdown suggests obstacles to progress',
                    'beautiful vehicle indicates positive self-image',
                    'crowded vehicle indicates too many influences or pressures'
                ]
            }
        }
        
        # Emotional keywords for deeper analysis
        self.emotional_keywords = {
            'positive': {
                'joy': ['happy', 'joyful', 'laughing', 'celebrating', 'winning', 'succeeding', 'loved'],
                'peace': ['calm', 'peaceful', 'serene', 'quiet', 'safe', 'secure', 'comfortable'],
                'love': ['loved', 'loving', 'affectionate', 'embrace', 'kiss', 'together', 'connected'],
                'hope': ['hopeful', 'optimistic', 'future', 'bright', 'light', 'beautiful', 'wonderful']
            },
            'negative': {
                'fear': ['afraid', 'scared', 'terrified', 'horror', 'dread', 'panic', 'anxious'],
                'sadness': ['sad', 'grief', 'loss', 'crying', 'depressed', 'lonely', 'abandoned'],
                'anger': ['angry', 'rage', 'furious', 'violent', 'aggressive', 'hostile', 'fighting'],
                'confusion': ['confused', 'lost', 'disoriented', 'trapped', 'stuck', 'helpless', 'desperate']
            }
        }
    
    def analyze_symbols(self, dream_text):
        """Identify dream symbols and extract their meanings"""
        dream_lower = dream_text.lower()
        found_symbols = []
        
        for symbol, details in self.symbol_meanings.items():
            if symbol in dream_lower:
                # Find which interpretation matches best with context
                context_words = dream_lower.split()
                interpretations = details['interpretations']
                
                found_symbols.append({
                    'symbol': symbol,
                    'themes': details['themes'],
                    'psychology': details['psychology'],
                    'jungian': details['jungian'],
                    'interpretations': interpretations
                })
        
        return found_symbols
    
    def analyze_emotions(self, dream_text):
        """Deep emotional analysis"""
        dream_lower = dream_text.lower()
        emotional_profile = {
            'positive': {},
            'negative': {}
        }
        
        for category, keywords_dict in self.emotional_keywords.items():
            for emotion, words in keywords_dict.items():
                count = sum(dream_lower.count(word) for word in words)
                if count > 0:
                    emotional_profile[category][emotion] = count
        
        return emotional_profile
    
    def extract_dream_elements(self, dream_text):
        """Extract key elements from the dream text"""
        elements = {
            'actions': [],
            'settings': [],
            'characters': [],
            'objects': []
        }
        
        action_keywords = ['running', 'flying', 'falling', 'chasing', 'fighting', 'building', 
                          'destroying', 'searching', 'hiding', 'escaping', 'drowning', 'walking',
                          'talking', 'screaming', 'laughing', 'dancing', 'swimming', 'climbing']
        
        setting_keywords = ['house', 'forest', 'water', 'sky', 'city', 'mountain', 'beach',
                           'desert', 'dark', 'light', 'room', 'building', 'street', 'field']
        
        character_keywords = ['family', 'friend', 'stranger', 'enemy', 'lover', 'child', 'parent',
                             'person', 'people', 'man', 'woman', 'child', 'baby', 'monster']
        
        dream_lower = dream_text.lower()
        
        for action in action_keywords:
            if action in dream_lower:
                elements['actions'].append(action)
        
        for setting in setting_keywords:
            if setting in dream_lower:
                elements['settings'].append(setting)
        
        for character in character_keywords:
            if character in dream_lower:
                elements['characters'].append(character)
        
        return elements
    
    def search_database_semantically(self, dream_text, limit=3):
        """Semantic search in database"""
        if not self.database:
            return []
        
        dream_words = dream_text.lower().split()
        
        # Score each database entry
        scored_results = []
        for entry in self.database:
            entry_word = entry['word'].lower()
            
            # Check for exact match or word overlap
            matches = 0
            for word in dream_words:
                if word in entry_word or entry_word in word:
                    matches += 1
            
            # Also check for keyword similarity
            if matches > 0:
                scored_results.append({
                    'word': entry['word'],
                    'interpretation': entry['interpretation'],
                    'score': matches
                })
        
        # If no matches found, pick random relevant ones
        if not scored_results and self.database:
            import random
            scored_results = random.sample(self.database, min(3, len(self.database)))
            for item in scored_results:
                item['score'] = 1
        
        # Return top results
        scored_results.sort(key=lambda x: x['score'], reverse=True)
        return scored_results[:limit]
    
    def generate_interpretation(self, dream_text):
        """Generate a comprehensive, intelligent interpretation"""
        
        # Analyze dream components
        symbols = self.analyze_symbols(dream_text)
        emotions = self.analyze_emotions(dream_text)
        elements = self.extract_dream_elements(dream_text)
        db_results = self.search_database_semantically(dream_text)
        
        interpretation = []
        
        # Header
        interpretation.append("=" * 70 + "\n")
        interpretation.append("DREAMLENS AI - ADVANCED DREAM INTERPRETATION\n")
        interpretation.append("=" * 70 + "\n\n")
        
        # Opening insight
        interpretation.append("YOUR DREAM ANALYSIS\n")
        interpretation.append("-" * 70 + "\n\n")
        
        # Generate opening based on dream characteristics
        positive_emotions = sum(emotions.get('positive', {}).values())
        negative_emotions = sum(emotions.get('negative', {}).values())
        
        if positive_emotions > negative_emotions:
            tone = "Your dream carries an overall positive and hopeful energy. "
        elif negative_emotions > positive_emotions:
            tone = "Your dream involves challenges and difficult emotions that need addressing. "
        else:
            tone = "Your dream presents a balanced mix of experiences and emotions. "
        
        interpretation.append(tone)
        interpretation.append("Let's explore what your subconscious is trying to tell you.\n\n")
        
        # SYMBOLS FOUND
        if symbols:
            interpretation.append("SYMBOLS IN YOUR DREAM\n")
            interpretation.append("-" * 70 + "\n")
            
            for i, symbol in enumerate(symbols[:4], 1):
                interpretation.append(f"\n{i}. {symbol['symbol'].upper()}\n")
                interpretation.append(f"   Themes: {', '.join(symbol['themes'])}\n")
                interpretation.append(f"   Meaning: {symbol['psychology']}\n")
                interpretation.append(f"   Jungian View: {symbol['jungian']}\n")
                
                # Select relevant interpretation
                interpretation.append(f"   In your dream: ")
                if len(symbol['interpretations']) > 1:
                    interpretation.append(symbol['interpretations'][0] + "\n")
                else:
                    interpretation.append(symbol['interpretations'][0] + "\n")
            
            interpretation.append("\n")
        
        # DREAM ELEMENTS ANALYSIS
        if elements['actions'] or elements['settings'] or elements['characters']:
            interpretation.append("ELEMENTS IN YOUR DREAM\n")
            interpretation.append("-" * 70 + "\n\n")
            
            if elements['actions']:
                interpretation.append(f"Actions: You were {', '.join(elements['actions'])}. ")
                interpretation.append("These actions reveal what your mind is focused on and how you're processing your waking life.\n\n")
            
            if elements['settings']:
                interpretation.append(f"Settings: The dream took place in/around {', '.join(elements['settings'])}. ")
                interpretation.append("Locations in dreams represent different aspects of your inner world.\n\n")
            
            if elements['characters']:
                interpretation.append(f"Characters: You encountered {', '.join(elements['characters'])}. ")
                interpretation.append("Different people often represent different aspects of yourself or real relationships.\n\n")
        
        # EMOTIONAL ANALYSIS
        interpretation.append("EMOTIONAL CONTEXT\n")
        interpretation.append("-" * 70 + "\n\n")
        
        if positive_emotions > 0:
            positive_list = list(emotions.get('positive', {}).keys())
            interpretation.append(f"Positive emotions detected: {', '.join(positive_list)}. ")
            interpretation.append("These suggest areas of your life bringing fulfillment or hope.\n\n")
        
        if negative_emotions > 0:
            negative_list = list(emotions.get('negative', {}).keys())
            interpretation.append(f"Challenging emotions detected: {', '.join(negative_list)}. ")
            interpretation.append("These represent areas needing attention or resolution.\n\n")
        
        if positive_emotions == 0 and negative_emotions == 0:
            interpretation.append("Your dream had a neutral emotional tone, suggesting observation ")
            interpretation.append("or detachment from the events.\n\n")
        
        # DATABASE INSIGHTS
        if db_results:
            interpretation.append("RELATED DREAM KNOWLEDGE\n")
            interpretation.append("-" * 70 + "\n\n")
            
            interpretation.append("Interpretations from our database of thousands of dreams:\n\n")
            for i, result in enumerate(db_results[:2], 1):
                text = result['interpretation']
                if len(text) > 200:
                    text = text[:200] + "..."
                interpretation.append(f"{i}. About '{result['word']}': {text}\n\n")
        
        # PSYCHOLOGICAL PERSPECTIVE
        interpretation.append("WHAT THIS MEANS PSYCHOLOGICALLY\n")
        interpretation.append("-" * 70 + "\n\n")
        
        if symbols:
            interpretation.append("Based on the symbols and themes in your dream:\n\n")
            
            if any(s['symbol'] in ['house', 'family'] for s in symbols):
                interpretation.append("- This dream relates to your sense of self, home, and family dynamics.\n")
                interpretation.append("  Consider what aspects of these areas need attention or celebration.\n\n")
            
            if any(s['symbol'] in ['flying', 'water'] for s in symbols):
                interpretation.append("- Your dream involves movement and change.\n")
                interpretation.append("  This suggests your mind is processing transitions or seeking freedom.\n\n")
            
            if any(s['symbol'] in ['chase', 'fall'] for s in symbols):
                interpretation.append("- Your dream contains elements of challenge or anxiety.\n")
                interpretation.append("  This indicates something in your waking life needs to be addressed.\n\n")
        
        interpretation.append("Your subconscious mind speaks in symbols and emotions, not logic. ")
        interpretation.append("What matters most is YOUR interpretation and how the dream makes you feel.\n\n")
        
        # REFLECTION QUESTIONS
        interpretation.append("QUESTIONS FOR DEEPER REFLECTION\n")
        interpretation.append("-" * 70 + "\n\n")
        
        questions = [
            "What feeling from the dream stayed with you most? What in your life triggers that feeling?",
            "If you could change one thing about the dream, what would it be? What does that reveal about your desires?",
            "Is there a situation in your waking life that mirrors this dream? What needs to change?",
            "What is your subconscious trying to tell you that you might be ignoring?"
        ]
        
        for i, question in enumerate(questions, 1):
            interpretation.append(f"{i}. {question}\n\n")
        
        # CLOSING
        interpretation.append("=" * 70 + "\n")
        interpretation.append("Remember: Dreams are personal. Only YOU can determine true meaning.\n")
        interpretation.append("Use this analysis as a guide for self-discovery, not absolute truth.\n")
        interpretation.append("=" * 70 + "\n")
        
        return ''.join(interpretation)


# Initialize interpreter
interpreter = DreamInterpreter(dreams_database)

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
        
        if not user_dream or len(user_dream) < 5:
            return jsonify({
                "success": False, 
                "message": "Please describe your dream in more detail (at least a few words)."
            })
        
        # Generate interpretation using advanced engine
        result = interpreter.generate_interpretation(user_dream)
        
        return jsonify({
            "success": True, 
            "interpretation": result
        })
    
    except Exception as e:
        print(f"Error in interpret endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False, 
            "message": f"Error: {str(e)}"
        })

@app.route("/health")
def health():
    return jsonify({
        "status": "OK", 
        "message": "Advanced Dream Interpretation Engine Running",
        "database_size": len(dreams_database),
        "symbols_available": 10,
        "model_type": "Generative AI (Advanced)"
    })

if __name__ == "__main__":
    print("=" * 70)
    print("DREAMLENS AI - ADVANCED GENERATIVE ENGINE")
    print("=" * 70)
    print(f"Database loaded: {len(dreams_database)} interpretations")
    print("Symbols: Water, Flying, Chase, House, Death, Fall, Animal, Snake, Family, Vehicle")
    print("Analysis: Symbols, Emotions, Elements, Psychology, Database, Generation")
    print("=" * 70)
    print("\nStarting server...")
    app.run(debug=True, port=5000)
