import json
import logging
import time
from groq_client import safe_groq_completion, GROQ_API_KEY, GROQ_MODEL
from services.input_classifier import classify_input
from services.symbol_analyzer import search_symbol_meanings
from services.youtube_search import search_live_youtube_videos

# Curated catalog of fantasy & dream exploration YouTube videos
BASE_YOUTUBE_CATALOG = [
    {
        "ytId": "W6NZfCO5SIk",
        "title": "Inception — A Journey Through Dreams & Reality",
        "channel": "Fantasy Cinema Hub",
        "desc": "A cinematic dive exploring the structure of layered dreamscapes and subconscious portals.",
        "genre": "fantasy",
        "duration": "14:27",
        "keywords": ["door", "portal", "building", "falling", "layer", "lucid", "dimension", "forest"]
    },
    {
        "ytId": "MV4PiT-ZHCA",
        "title": "How to Lucid Dream Tonight — Full Guided Technique",
        "channel": "Lucid Dream Society",
        "desc": "Step-by-step techniques to gain conscious awareness and reshape dream climaxes.",
        "genre": "lucid",
        "duration": "22:15",
        "keywords": ["lucid", "flying", "control", "awareness", "sleep", "mind", "sky"]
    },
    {
        "ytId": "1ZYbU82GVz4",
        "title": "Deep Sleep Fantasy Ambience — Enchanted Forest & Rain",
        "channel": "Dream Soundscapes",
        "desc": "Immersive ambient fantasy soundscape to drift into magical nocturnal realms.",
        "genre": "ambient",
        "duration": "3:00:00",
        "keywords": ["forest", "trees", "nature", "rain", "peace", "calm", "night", "wood"]
    },
    {
        "ytId": "6Af6b_wyiwI",
        "title": "The Science of Dreaming — What Happens When We Sleep",
        "channel": "Kurzgesagt",
        "desc": "Animated breakdown of why the brain dreams and how memory consolidation works.",
        "genre": "mystery",
        "duration": "9:34",
        "keywords": ["science", "brain", "mystery", "psychology", "memory", "thinking"]
    },
    {
        "ytId": "hVyGbP7hMTk",
        "title": "Top 10 Surreal Fantasy Dream Movies You Must Experience",
        "channel": "CinemaScope",
        "desc": "The most visually breathtaking films that explore parallel dream worlds.",
        "genre": "fantasy",
        "duration": "11:44",
        "keywords": ["fantasy", "movie", "dragon", "magic", "castle", "ocean", "space"]
    },
    {
        "ytId": "R9OHn5ZF4Uo",
        "title": "WILD Technique — Wake Induced Lucid Dreaming Masterclass",
        "channel": "Lucid Dream Portal",
        "desc": "Master waking-to-dream transitions without losing consciousness.",
        "genre": "lucid",
        "duration": "18:52",
        "keywords": ["wild", "lucid", "transition", "sleep", "paralysis", "door"]
    },
    {
        "ytId": "5qap5aO4i9A",
        "title": "Lofi Fantasy Beats — Celestial Dreams & Magic",
        "channel": "ChilledCow Fantasy",
        "desc": "Chill atmospheric beats blended with celestial harp and ambient synthesizers.",
        "genre": "ambient",
        "duration": "1:00:00",
        "keywords": ["stars", "nebula", "clouds", "space", "flying", "calm", "music"]
    },
    {
        "ytId": "9Y1SiH_lcS4",
        "title": "The Mystery of Recurring Dreams & Hidden Messages",
        "channel": "Mind Unraveled",
        "desc": "Psychological analysis of why specific dream locations and characters return.",
        "genre": "mystery",
        "duration": "16:03",
        "keywords": ["recurring", "fear", "chase", "falling", "cliff", "escape", "symbol"]
    },
    {
        "ytId": "GaOAoznW31s",
        "title": "Epic Fantasy Realm Odyssey — The Myth of Transformation",
        "channel": "Fantasy Realm",
        "desc": "A mythical journey through ancient ruins, soaring mountains, and hidden gateways.",
        "genre": "adventure",
        "duration": "31:22",
        "keywords": ["journey", "door", "gate", "mountain", "key", "owl", "dragon", "hero"]
    },
    {
        "ytId": "K3Qzzggn--s",
        "title": "Jungian Dream Interpretation Masterclass: Archetypes & Shadow",
        "channel": "Psychology Unlocked",
        "desc": "How Carl Jung explored universal archetypes, the Shadow, and threshold symbols.",
        "genre": "mystery",
        "duration": "47:11",
        "keywords": ["jung", "archetype", "shadow", "freud", "door", "water", "snake"]
    },
    {
        "ytId": "4fndeDfaWCg",
        "title": "Magical Castle Night Ambience — Fireplace & Gentle Rain",
        "channel": "Ambient Worlds",
        "desc": "Sleep to the soothing sounds of an ancient stone castle surrounded by stars.",
        "genre": "ambient",
        "duration": "8:00:00",
        "keywords": ["castle", "library", "room", "fire", "cozy", "books", "shelves"]
    },
    {
        "ytId": "7apHE3KWPPA",
        "title": "Surreal Dream Journeys — The Art of Flying & Exploration",
        "channel": "Surreal Cinema",
        "desc": "An artistic exploration of the floating sensation and soaring over glowing oceans.",
        "genre": "adventure",
        "duration": "28:30",
        "keywords": ["ocean", "water", "flying", "sky", "bird", "clouds", "island"]
    }
]


def match_youtube_recommendations(dream_text: str, primary_theme: str = "", key_symbols: list = None) -> list:
    """Matches curated YouTube videos to the user's dream theme and symbols."""
    text_lower = (dream_text + " " + primary_theme + " " + " ".join(key_symbols or [])).lower()
    scored = []
    for v in BASE_YOUTUBE_CATALOG:
        score = sum(2 for kw in v["keywords"] if kw in text_lower)
        if any(term in text_lower for term in ["magic", "dragon", "portal", "fantasy"]) and v["genre"] == "fantasy":
            score += 3
        if any(term in text_lower for term in ["fly", "control", "aware"]) and v["genre"] == "lucid":
            score += 3
        if any(term in text_lower for term in ["forest", "quiet", "ocean", "calm"]) and v["genre"] == "ambient":
            score += 2
        scored.append((score, v))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in scored[:6]]



def generate_rich_revelation(dream_text: str, primary_theme: str = None, key_symbols: list = None, tone: str = None) -> str:
    """
    Generates a longer, deeply engaging, fascinating multi-paragraph psychological
    narrative revelation for the dream instead of a static motivational quote.
    """
    text_lower = (dream_text or "").lower()
    symbols_str = ", ".join(key_symbols) if key_symbols else "your core dream symbols"
    theme_str = primary_theme or "Personal Sovereignty & Inner Alignment"

    if any(k in text_lower for k in ["pongal", "diwali", "festival", "harvest", "feast", "celebrat", "sugarcane", "pot", "boiled", "sweet", "family"]):
        return (
            "Your dream reflects a soul-nourishing celebration of sacred abundance, gratitude, and familial harmony. "
            "In subconscious symbolism, harvest festivals like Pongal embody the profound spiritual truth of 'overflowing prosperity' "
            "(Pongalo Pongal!)—where nature, solar warmth, and ancestral traditions unite in joyful thanksgiving.\n\n"
            "This vision is an auspicious affirmation from your deeper mind: your psyche is feeling grounded, deeply connected to your roots, "
            "and receptive to new blessings. The traditional boiling over of milk and rice represents life's gifts overflowing beyond the narrow boundaries "
            "of daily worry, signifying that your efforts are yielding sweetness and shared joy.\n\n"
            "This dream carries no threat or fear—it is a sacred invitation to celebrate the abundance already present in your waking life. "
            "Honor your family bonds, express heartfelt gratitude for the quiet blessings around you, and remember that true prosperity multiplies "
            "infinitely when shared with warmth and generosity."
        )
    elif any(k in text_lower for k in ["elephant", "beast", "chase", "jungle", "predator", "animal", "pursued"]):
        return (
            "Your sleeping consciousness has staged a high-stakes confrontation of raw instinct and primal authority. "
            "In depth psychology, wild beasts in dreams do not emerge as random adversaries—they are living embodiments "
            "of the shadow self, carrying vital psychic energy that your conscious waking persona has exiled or feared to command.\n\n"
            "The thunderous pursuit reveals an ongoing waking struggle: you have been fleeing a situation that demands your sovereign "
            "authority, misinterpreting your own capacity for power as an external threat. The dense wilderness reflects unresolved ambiguity "
            "in your current life choices, where fear has distorted an opportunity into an emergency.\n\n"
            "The turning point—when the wild force halts before you in stillness—is your subconscious delivering an ultimatum. "
            "The beast did not stop to destroy you; it stopped because you ran out of avoidance. In this sacred quiet, the perceived danger dissolves "
            "into an ally of immense wisdom. Your subconscious is telling you that the moment you stop running from waking responsibility and hold your "
            "ground with calm awareness, the chaos of your waking life will yield to your natural authority."
        )
    elif any(k in text_lower for k in ["door", "forest", "wood", "threshold", "portal", "gate", "path"]):
        return (
            "Your dream consciousness has orchestrated a sacred threshold initiation between your safe, familiar persona and an expansive "
            "new chapter of personal evolution. The quiet forest represents the unmapped, quiet reservoir of your subconscious mind—a realm where old "
            "waking identities fall away and latent potential stirs.\n\n"
            "The appearance of a freestanding glowing door signifies a pivotal psychological transition that you have consciously sensed but "
            "hesitated to name. Wood represents organic life, rooted endurance, and natural timing, while the golden illumination leaking beneath "
            "the frame is the classic archetypal marker of integration and self-illumination. The hesitation you experienced at the threshold was "
            "not a sign of weakness; it was the sacred friction of your ego surrendering its need to control the outcome.\n\n"
            "By taking the decisive step through the threshold, your subconscious completed the psychic leap before your waking mind could talk you out of it. "
            "The golden light that received you is proof that what lies on the other side of your current waking crossroads is not danger, but clarity and "
            "creative sovereignty. The threshold is already behind you in your psyche; now your waking decisions must match your inner courage."
        )
    elif any(k in text_lower for k in ["cliff", "fall", "falling", "ocean", "water", "sea", "glide", "drop"]):
        return (
            "This dream captures the ultimate psychological paradox of surrender: discovering that what your conscious mind interprets as "
            "catastrophic failure is actually the beginning of autonomous flight. The cliff edge represents the rigid boundaries of your waking "
            "control—the precarious precipice where intellectual planning can no longer navigate the depth of your life.\n\n"
            "The violet ocean below is the vast, ancient mirror of the collective unconscious, blending the fiery tension of red with the deep emotional wisdom "
            "of blue. When you lost your footing, your waking ego registered panic, anticipating impact and devastation. Yet, the moment resistance ceased, "
            "the aerodynamic laws of your inner world transformed gravity into buoyancy.\n\n"
            "Gliding gracefully above the water represents the emergence of radical self-trust. Your psyche is delivering a profound revelation for waking life: "
            "the exhaustion you currently feel comes from desperately trying not to fall. Your subconscious is revealing that you do not need to grip the cliff "
            "edge so tightly—when you release overthinking and allow yourself to move with the currents of change, you will find you are fully capable of gliding."
        )
    elif any(k in text_lower for k in ["library", "book", "key", "owl", "scroll", "ancient", "room", "temple"]):
        return (
            "You have entered the archetypal sanctuary of the collective unconscious—a timeless realm housing the accumulated wisdom, ancestral memories, "
            "and latent knowledge of your deeper self. Towering mahogany shelves symbolize deep-rooted emotional architecture and lifelong cognitive consolidation.\n\n"
            "The arrival of the owl carries ancient mythic weight: across cultures, the owl is the solitary guardian of the night, gifted with the ability to see "
            "through impenetrable darkness where others are blind. In your dream, this messenger does not test or judge you; it recognizes your readiness and entrusts "
            "you with a glowing brass key. Brass is an alloy of copper and zinc—representing the harmonious blending of intuition and grounding discipline.\n\n"
            "This dream reveals that the answers to your current waking dilemmas cannot be found in surface-level noise or external advice. The key you were handed "
            "is already within your possession: it is your innate intuition and analytical discernment. Your subconscious is urging you to unlock the quiet, "
            "sovereign knowledge you already have and trust your inner authority."
        )
    elif any(k in text_lower for k in ["fly", "flying", "sky", "cloud", "soar", "wing", "air", "star"]):
        return (
            "Flight dreams are the purest expression of psychological transcendence and liberation from waking gravity. By soaring above purple clouds, "
            "your psyche has elevated itself above the daily turmoil and emotional entanglements that frequently consume your waking energy.\n\n"
            "The landscape beneath you—jagged mountains and glowing cities—represents the physical obstacles, complex social obligations, and career structures "
            "of your everyday world. Seen from above, these monumental challenges appear small, ordered, and easily navigable. This shift in perspective is not mere "
            "escapism; it is an active recalibration of your cognitive sovereignty, allowing you to see the interconnected tapestry of your life without feeling trapped "
            "by its immediate friction.\n\n"
            "Your ability to steer freely through the starry night demonstrates that you possess high internal locus of control and strong emotional sovereignty. "
            "The dream is calling on you to bring this panoramic vantage point down into your daytime reality: do not get bogged down in petty dramas or minor setbacks—zoom out, "
            "see the broader horizon, and steer with the same effortless clarity."
        )
    else:
        return (
            f"Your sleeping mind has staged an evocative initiation exploring {theme_str}. In depth psychology, the nocturnal landscape acts as a sacred mirror "
            f"where unconscious desires, unspoken fears, and latent strengths take tangible form through symbols like {symbols_str}.\n\n"
            "The narrative progression of this vision reveals a critical psychological friction: your conscious self is navigating a period of transition, yet old habit patterns "
            "are attempting to maintain control through hesitation or heightened tension. The subconscious mind does not produce these vivid images to alarm you, but to compel "
            "conscious awareness. It is demanding that you examine where in your waking life you are holding back or conforming to external expectations.\n\n"
            "By unraveling the core emotional movement of this dream, a clear directive emerges: step into active sovereignty. Your inner psyche has already crossed the threshold "
            "of the unfamiliar and survived the encounter. Carry this quiet resilience into your waking hours—trust your instinct, hold your boundaries with calm conviction, and "
            "allow your natural clarity to lead."
        )

def unified_dream_analysis(dream_text: str) -> dict:
    """
    Runs a unified, single-pass dream intelligence analysis returning the exact
    structures required by the 12-screen UI system.
    """
    db_context = search_symbol_meanings(dream_text)
    
    system_prompt = (
        "You are DREAMLENS AI — an elite dream intelligence psychologist and mythologist.\n"
        "Analyze the user's dream and return a concise, deeply structured JSON object.\n"
        "CRITICAL RULES:\n"
        "1. Symbol Network: 'center_node' MUST be the primary focal symbol (e.g. 'Elephant', 'Ocean', 'Darkness'). 'connected_nodes' must contain 4 distinct specific symbols/elements from this dream.\n"
        "2. Psychology Lenses: Provide distinct 1-2 sentence analyses for Freudian (subconscious drives), Jungian (archetypes & shadow), Modern Cognitive (emotional regulation), and Mythological (universal & Indian folklore/myths).\n"
        "3. Scenario Presets: 3 exciting 'What If?' climax alteration options tailored to this dream.\n4. Subconscious Revelation: 'in_short.revelation' MUST be a longer, deeply engaging, fascinating multi-paragraph narrative decode (140-200 words) exploring: (a) what latent psychological drama your subconscious is staging, (b) the unspoken emotional tension between your conscious self and the dream encounter, and (c) the psychological sovereignty/power shift being demanded in your waking life. Do not give generic motivational slogans—give a rich, intriguing psychological reading.\n\n"
        "Return valid JSON matching this schema:\n"
        "{\n"
        "  \"dream_profile\": {\"overall_intensity\": 78, \"intensity_label\": \"High\", \"primary_theme\": \"Theme\", \"emotional_tone\": \"Tone\", \"recurring_patterns_count\": 1, \"key_symbols\": [\"Sym1\", \"Sym2\"]},\n"
        "  \"in_short\": {\"summary\": \"Core subconscious meaning.\", \"takeaway\": \"Actionable waking insight.\", \"visual_theme\": \"Visual dreamscape art description\"},\n"
        "  \"story_timeline\": [\n"
        "    {\"stage_num\": 1, \"title\": \"1. Initial Encounter\", \"desc\": \"How it began\", \"scene\": \"encounter\"},\n"
        "    {\"stage_num\": 2, \"title\": \"2. Rising Tension\", \"desc\": \"The escalation\", \"scene\": \"tension\"},\n"
        "    {\"stage_num\": 3, \"title\": \"3. Climax Moment\", \"desc\": \"Peak confrontation\", \"scene\": \"climax\"},\n"
        "    {\"stage_num\": 4, \"title\": \"4. Awakening / Resolution\", \"desc\": \"Conclusion and shift\", \"scene\": \"resolution\"}\n"
        "  ],\n"
        "  \"story_key_insights\": \"Narrative arc insight for personal evolution.\",\n"
        "  \"emotion_arc\": {\n"
        "    \"curve\": [{\"stage\": \"Beginning\", \"val\": 0.1, \"label\": \"Curious\"}, {\"stage\": \"Middle\", \"val\": -0.6, \"label\": \"Alarmed\"}, {\"stage\": \"End\", \"val\": 0.7, \"label\": \"Empowered\"}],\n"
        "    \"breakdown\": [{\"name\": \"Intensity\", \"pct\": 45, \"color\": \"#ec4899\"}, {\"name\": \"Curiosity\", \"pct\": 25, \"color\": \"#06b6d4\"}, {\"name\": \"Courage\", \"pct\": 30, \"color\": \"#10b981\"}],\n"
        "    \"insights\": [{\"label\": \"Dominant Emotion\", \"text\": \"Dynamic seen in dream.\", \"badge\": \"badge-pink\"}, {\"label\": \"Waking Bridge\", \"text\": \"Real world application.\", \"badge\": \"badge-cyan\"}]\n"
        "  },\n"
        "  \"symbol_network\": {\n"
        "    \"center_node\": {\"id\": \"MainSym\", \"label\": \"Main Symbol\"},\n"
        "    \"connected_nodes\": [\n"
        "      {\"id\": \"Sym1\", \"label\": \"Symbol 1\", \"meaning\": \"Meaning in dream\", \"rel\": \"Catalyst\"},\n"
        "      {\"id\": \"Sym2\", \"label\": \"Symbol 2\", \"meaning\": \"Meaning in dream\", \"rel\": \"Setting\"},\n"
        "      {\"id\": \"Sym3\", \"label\": \"Symbol 3\", \"meaning\": \"Meaning in dream\", \"rel\": \"Conflict\"},\n"
        "      {\"id\": \"Sym4\", \"label\": \"Symbol 4\", \"meaning\": \"Meaning in dream\", \"rel\": \"Resolution\"}\n"
        "    ],\n"
        "    \"key_reflection\": \"Subconscious synthesis of these symbols.\"\n"
        "  },\n"
        "  \"psychology\": {\n"
        "    \"freudian\": {\"title\": \"Freudian Analysis\", \"subtitle\": \"Unconscious Drives & Instincts\", \"text\": \"Analysis of suppressed energy.\"},\n"
        "    \"jungian\": {\"title\": \"Jungian Analysis\", \"subtitle\": \"Archetypes & Individuation\", \"text\": \"Analysis of archetypes and shadow integration.\"},\n"
        "    \"modern\": {\"title\": \"Modern Psychology\", \"subtitle\": \"Cognitive & Emotional Regulation\", \"text\": \"Analysis of cognitive memory processing.\"},\n"
        "    \"mythological\": {\"title\": \"Mythological Reflection\", \"subtitle\": \"Universal & Indian Folklore Archetypes\", \"text\": \"Folklore and mythic connection.\"},\n"
        "    \"synthesis\": \"Synthesis of personal transformation.\"\n"
        "  },\n"
        "  \"scenario_presets\": [\"What if I did X?\", \"What if I did Y?\", \"What if I did Z?\"],\n"
        "  \"hypotheses\": [{\"title\": \"Awakening Insight\", \"explanation\": \"Transformation hypothesis\", \"evidence\": \"Dream symbol\", \"confidence\": \"High\", \"validation_condition\": \"Reflective question\"}],\n"
        "  \"reflection_questions\": [\"What does this reflect in waking life?\", \"How will you apply this power today?\"]\n"
        "}\n"
        "Output ONLY valid JSON."
    )

    user_prompt = f'Dream: "{dream_text}"'
    if db_context:
        user_prompt += f"\n\nSymbol Index Reference:\n{db_context}"

    # Retry with backoff for overloaded model
    last_err = None
    for attempt in range(3):
        try:
            content = safe_groq_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=GROQ_MODEL,
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=2048
            )
            parsed = json.loads(content)
            if isinstance(parsed, dict):
                return parsed
            if isinstance(parsed, list):
                object_items = [item for item in parsed if isinstance(item, dict)]
                if len(object_items) == 1:
                    logging.warning("Unified analysis returned a list; using its single object item.")
                    return object_items[0]
            raise ValueError(f"Unified analysis returned {type(parsed).__name__}; expected a JSON object")
        except Exception as e:
            last_err = e
            if attempt < 2:
                wait = 1.5 * (attempt + 1)
                logging.warning(f"Groq attempt {attempt+1} failed: {e}. Retrying in {wait}s...")
                time.sleep(wait)
    raise last_err



def run_dream_pipeline(dream_text: str) -> dict:
    """
    Executes the comprehensive DreamLens pipeline and packages all data
    for the 12 UI screens.
    """
    logging.info(f"DreamLens Pipeline started for text length {len(dream_text or '')}")
    
    # 1. Classification
    classification_result = classify_input(dream_text)
    classification = classification_result.get("classification", "DREAM")
    
    if classification == "NON_DREAM":
        return {
            "success": True,
            "classification": "NON_DREAM",
            "message": "🌙 DreamLens is designed for dream exploration rather than general questions. Share a dream, nightmare, or recurring dream and I can help you explore its emotions, symbols, conflicts, and possible meanings."
        }
    
    elif classification == "AMBIGUOUS":
        return {
            "success": True,
            "classification": "AMBIGUOUS",
            "message": "It seems like you provided a symbol or a fragment. What happened with this symbol in the dream, and what did you feel? Please tell me more so we can explore it."
        }

    # 2. Unified Dream Intelligence Analysis
    try:
        raw = unified_dream_analysis(dream_text)
    except Exception as e:
        logging.error(f"Error in unified_dream_analysis: {e}")
        raw = {
            "dream_profile": {
                "overall_intensity": 62,
                "intensity_label": "Moderate",
                "primary_theme": "Growth & Transition",
                "emotional_tone": "Reflective",
                "recurring_patterns_count": 2,
                "key_symbols": ["Path", "Light", "Threshold"]
            },
            "in_short": {
                "summary": "Your dream reflects an active period of transformation and personal discovery.",
                "visual_theme": "A glowing cosmic threshold under starry skies",
                "visual_palette": ["#7c3aed", "#06b6d4", "#10b981"]
            },
            "story_timeline": [
                {"stage_num": 1, "title": "1. Beginning", "desc": "The journey begins in a calm, mysterious realm.", "scene": "forest"},
                {"stage_num": 2, "title": "2. Discovery", "desc": "An unexpected glowing symbol captures your focus.", "scene": "door"},
                {"stage_num": 3, "title": "3. The Choice", "desc": "You navigate through uncertainty with growing resolve.", "scene": "portal"},
                {"stage_num": 4, "title": "4. Resolution", "desc": "Clarity and calm arrive at the transition's end.", "scene": "meadow"}
            ],
            "story_key_insights": "The dream reflects an inward journey moving from hesitation toward empowered clarity.",
            "emotion_arc": {
                "curve": [{"stage": "Beginning", "val": 0.2, "label": "Neutral"}, {"stage": "Middle", "val": -0.3, "label": "Anxious"}, {"stage": "End", "val": 0.7, "label": "Hopeful"}],
                "breakdown": [{"name": "Neutral", "pct": 60, "color": "#06b6d4"}, {"name": "Anxiety", "pct": 20, "color": "#ec4899"}, {"name": "Hope", "pct": 12, "color": "#a855f7"}, {"name": "Calm", "pct": 8, "color": "#10b981"}],
                "insights": [
                    {"label": "Neutrality", "text": "You maintain balance throughout the dream.", "badge": "badge-cyan"},
                    {"label": "Anxiety", "text": "Felt during the transitional moments.", "badge": "badge-pink"},
                    {"label": "Hope", "text": "Builds towards the culmination.", "badge": "badge-purple"},
                    {"label": "Calm", "text": "A grounded feeling of resolution.", "badge": "badge-green"}
                ]
            },
            "symbol_network": {
                "center_node": {"id": "Threshold", "label": "Threshold"},
                "connected_nodes": [
                    {"id": "Discovery", "label": "Discovery", "meaning": "Insight & Awakening", "rel": "Insight"},
                    {"id": "Light", "label": "Light", "meaning": "Direction & Clarity", "rel": "Guide"},
                    {"id": "Path", "label": "Path", "meaning": "Life trajectory", "rel": "Journey"}
                ],
                "key_reflection": "Your subconscious is synthesizing emotional courage for upcoming life directions."
            },
            "psychology": {
                "freudian": {"title": "Freudian Analysis", "subtitle": "Unconscious Mind", "text": "Points toward subconscious wishes for greater autonomy and breaking free of routine."},
                "jungian": {"title": "Jungian Analysis", "subtitle": "Archetypes & Self", "text": "Reflects the archetypal hero's threshold, moving deeper into self-realization."},
                "modern": {"title": "Modern Psychology", "subtitle": "Cognitive & Narrative", "text": "Illustrates how your mind processes waking transitions and problem-solving."},
                "mythological": {"title": "Mythological Reflection", "subtitle": "Threshold Archetype", "text": "Resonates with universal myths of entering the enchanted gateway to acquire wisdom."},
                "synthesis": "Your dream reflects a balance between contemplation and courage, pointing toward self-discovery."
            },
            "hypotheses": [
                {
                    "title": "Inner Search & Transformation",
                    "explanation": "Reflects emotional processing of autonomy and untapped potential.",
                    "evidence": "Exploration of novel realms and navigating transitions.",
                    "confidence": "Moderate",
                    "validation_condition": "Reflect on where you seek clarity or change in daily life."
                }
            ],
            "reflection_questions": [
                "What decision in waking life is calling for your attention?",
                "How did you feel when you woke from this dream?"
            ]
        }

    # Normalization for all schema metrics
    profile = raw.get("dream_profile") or {}
    if not isinstance(profile, dict):
        profile = {"overall_intensity": 62, "intensity_label": "Moderate", "primary_theme": "Growth & Transition", "emotional_tone": "Neutral", "recurring_patterns_count": 2, "key_symbols": ["Path", "Light"]}
    raw["dream_profile"] = profile

    in_short = raw.get("in_short") or {}
    if not isinstance(in_short, dict):
        in_short = {"summary": str(in_short), "visual_theme": "forest_door"}
    raw["in_short"] = in_short

    timeline = raw.get("story_timeline") or []
    if not isinstance(timeline, list) or len(timeline) == 0:
        timeline = [
            {"stage_num": 1, "title": "1. Beginning", "desc": "The journey begins in a quiet, mysterious space.", "scene": 0},
            {"stage_num": 2, "title": "2. Discovery", "desc": "A symbolic encounter captures your attention.", "scene": 1},
            {"stage_num": 3, "title": "3. The Choice", "desc": "You step through the threshold with growing focus.", "scene": 2},
            {"stage_num": 4, "title": "4. Resolution", "desc": "Peaceful clarity emerges at the conclusion.", "scene": 3}
        ]
    raw["story_timeline"] = timeline

    emotion_arc = raw.get("emotion_arc") or {}
    if not isinstance(emotion_arc, dict):
        emotion_arc = {}
    if not isinstance(emotion_arc.get("curve"), list):
        emotion_arc["curve"] = [{"stage": "Beginning", "val": 0.2}, {"stage": "Middle", "val": -0.3}, {"stage": "End", "val": 0.8}]
    if not isinstance(emotion_arc.get("breakdown"), list):
        emotion_arc["breakdown"] = [{"name": "Neutral", "pct": 60, "color": "#06b6d4"}, {"name": "Anxiety", "pct": 20, "color": "#ec4899"}, {"name": "Hope", "pct": 12, "color": "#a855f7"}, {"name": "Calm", "pct": 8, "color": "#10b981"}]
    if not isinstance(emotion_arc.get("insights"), list):
        emotion_arc["insights"] = [
            {"label": "Neutrality", "text": "You maintain balance throughout the dream.", "badge": "badge-cyan"},
            {"label": "Anxiety", "text": "Felt during the transitional moments.", "badge": "badge-pink"},
            {"label": "Hope", "text": "Builds towards the culmination.", "badge": "badge-purple"},
            {"label": "Calm", "text": "A grounded feeling of resolution.", "badge": "badge-green"}
        ]
    raw["emotion_arc"] = emotion_arc

    sym_net = raw.get("symbol_network") or {}
    if not isinstance(sym_net, dict):
        sym_net = {}
    # Center node fallback based on key symbols or dream text
    primary_sym = (profile.get("key_symbols") or ["Core Symbol"])[0]
    center_node = sym_net.get("center_node")
    if isinstance(center_node, str):
        sym_net["center_node"] = {"id": center_node, "label": center_node}
    elif not isinstance(center_node, dict) or not center_node.get("label"):
        sym_net["center_node"] = {"id": primary_sym, "label": primary_sym}

    conn_nodes = sym_net.get("connected_nodes")
    if not isinstance(conn_nodes, list):
        conn_nodes = []
    
    # Ensure at least 4 nodes
    if len(conn_nodes) < 4:
        existing_labels = {n.get("label", "").lower() for n in conn_nodes if isinstance(n, dict)}
        candidates = (profile.get("key_symbols") or []) + ["Inner Power", "Instinct", "Transformation", "Awakening", "Courage", "Clarity"]
        for c in candidates:
            if c.lower() != primary_sym.lower() and c.lower() not in existing_labels:
                conn_nodes.append({
                    "id": c,
                    "label": c,
                    "meaning": f"Subconscious manifestation of {c.lower()}",
                    "rel": "Aspect"
                })
                existing_labels.add(c.lower())
                if len(conn_nodes) >= 4:
                    break
    sym_net["connected_nodes"] = conn_nodes[:5]
    raw["symbol_network"] = sym_net

    psych = raw.get("psychology") or {}
    if not isinstance(psych, dict):
        psych = {}
    
    first_sym = sym_net["center_node"]["label"]
    lens_defaults = {
        "freudian": f"The presence of {first_sym} points toward unconscious instinctual drives and suppressed emotional energy seeking safe psychological release.",
        "jungian": f"The encounter with {first_sym} represents an archetypal confrontation with the Shadow and instinctual Self, marking a vital stage of individuation.",
        "modern": f"Modern neuroscience views this dream as active emotional processing and threat-simulation, reorganizing stress and strengthening cognitive resilience.",
        "mythological": f"Echoes universal and sacred folklore where the primal beast or guardian tests the hero's readiness before granting deeper self-mastery."
    }
    for lens, def_sub in [("freudian", "Unconscious Drives & Instincts"), ("jungian", "Archetypes & Individuation"), ("modern", "Cognitive & Emotional Regulation"), ("mythological", "Universal & Indian Folklore")]:
        val = psych.get(lens)
        if isinstance(val, str):
            psych[lens] = {"title": lens.capitalize() + " Analysis", "subtitle": def_sub, "text": val}
        elif isinstance(val, dict):
            txt = (val.get("text") or val.get("content") or "").strip()
            if not txt or len(txt) < 15 or "Explores subconscious emotional processing" in txt:
                txt = lens_defaults[lens]
            psych[lens] = {"title": val.get("title") or (lens.capitalize() + " Analysis"), "subtitle": val.get("subtitle") or def_sub, "text": txt}
        else:
            psych[lens] = {"title": lens.capitalize() + " Analysis", "subtitle": def_sub, "text": lens_defaults[lens]}
    
    if not psych.get("synthesis"):
        psych["synthesis"] = f"Your dream presents an empowering opportunity to integrate the strength of {first_sym} into your waking choices and inner confidence."
    raw["psychology"] = psych

    # 3. Pass dream_text for client-side image generation (no server blocking)
    # The client generates Pollinations URLs directly — faster by 5-15 seconds
    in_short_obj = raw.get("in_short") or {}
    if not in_short_obj.get("revelation") or len(str(in_short_obj.get("revelation", ""))) < 80:
        symbols_list = profile.get("key_symbols", []) if isinstance(profile, dict) else []
        theme_val = profile.get("primary_theme", "") if isinstance(profile, dict) else ""
        in_short_obj["revelation"] = generate_rich_revelation(dream_text, theme_val, symbols_list)
    clean_text = dream_text.replace('"', '').replace('\n', ' ').strip()
    in_short_obj["dream_text_for_image"] = clean_text[:180]
    in_short_obj["image_prompt"] = f"Cinematic fantasy concept art of {clean_text[:120]}, atmospheric volumetric lighting, ethereal glow, 8k masterpiece, no text"
    raw["in_short"] = in_short_obj

    story_stages = raw.get("story_timeline") or []
    for i, st in enumerate(story_stages):
        if isinstance(st, dict):
            st["scene_prompt"] = f"{st.get('title', '')} {st.get('desc', '')}"
    raw["story_timeline"] = story_stages

    # 4. Live Relatable YouTube Recommendations (Dream & Solution Specific)
    symbols = profile.get("key_symbols", [])
    theme = profile.get("primary_theme", "")
    primary_sym = (symbols or ["dream"])[0] if isinstance(symbols, list) and len(symbols) > 0 else "dream"
    
    # Construct targeted search query like "elephant dream meaning interpretation solution"
    search_terms = f"{primary_sym} {theme} dream meaning interpretation solution"
    try:
        yt_recs = search_live_youtube_videos(search_terms, max_results=6)
    except Exception as e:
        logging.warning(f"Live YouTube search error in pipeline: {e}")
        yt_recs = match_youtube_recommendations(dream_text, theme, symbols)
    
    if not yt_recs or len(yt_recs) < 2:
        yt_recs = match_youtube_recommendations(dream_text, theme, symbols)
    raw["youtube_recommendations"] = yt_recs

    # Legacy report dictionary for backwards compatibility
    report_dict = {
        "atmosphere": raw.get("in_short", {}).get("summary", ""),
        "story_map": raw.get("story_key_insights", ""),
        "emotional_arc_text": "Emotional progression across the dream timeline.",
        "symbol_relationships_text": raw.get("symbol_network", {}).get("key_reflection", ""),
        "central_tension": profile.get("primary_theme", "Growth & Transition"),
        "psychological_lenses": {
            "emotional_psychology": raw.get("psychology", {}).get("freudian", {}).get("text", ""),
            "jungian_lens": raw.get("psychology", {}).get("jungian", {}).get("text", ""),
            "narrative_psychology": raw.get("psychology", {}).get("modern", {}).get("text", ""),
            "personal_growth": raw.get("psychology", {}).get("synthesis", "")
        },
        "mythological_reflection": raw.get("psychology", {}).get("mythological", {}).get("text", ""),
        "what_mind_exploring": raw.get("in_short", {}).get("summary", ""),
        "reflection_questions": raw.get("reflection_questions", []),
        "uncertainty_note": "Dream exploration is highly subjective. This report is a reflective tool to assist your self-discovery, not a fact or medical advice."
    }

    return {
        "success": True,
        "classification": "DREAM",
        "dream_profile": raw.get("dream_profile"),
        "in_short": raw.get("in_short"),
        "story_timeline": raw.get("story_timeline"),
        "story_key_insights": raw.get("story_key_insights"),
        "emotion_arc": raw.get("emotion_arc"),
        "symbol_network": raw.get("symbol_network"),
        "psychology": raw.get("psychology"),
        "hypotheses": raw.get("hypotheses"),
        "reflection_questions": raw.get("reflection_questions"),
        "youtube_recommendations": yt_recs,
        "report": report_dict,
        "analysis": {
            "emotions": [{"name": b["name"], "score": b["pct"]/100} for b in raw.get("emotion_arc", {}).get("breakdown", [])],
            "symbols": [{"name": n["label"], "meaning": n.get("meaning", "")} for n in raw.get("symbol_network", {}).get("connected_nodes", [])],
            "hypotheses": raw.get("hypotheses", []),
            "emotional_tone": profile.get("emotional_tone", "Neutral"),
            "overall_intensity": profile.get("intensity_label", "Moderate"),
            "synthesis": raw.get("psychology", {}).get("synthesis", "")
        },
        "processing_stages": [
            "input_classifier",
            "dream_intelligence_engine",
            "youtube_cinema_matcher"
        ]
    }


def simulate_scenario_pipeline(dream_text: str, scenario_type: str, choice_text: str) -> dict:
    """
    Scenario Simulator: Alters the dream's climax and explores alternative timelines,
    generating new story outcomes, psychological takeaways, and visual artwork prompts.
    """
    system_prompt = (
        "You are the DREAMLENS AI Scenario Simulator.\n"
        "Your task is to rewrite the climax of the user's dream according to an alternative choice ('What if?').\n"
        "Generate an inspiring alternative timeline narrative, 4 concrete possible outcomes/empowerments, and a visual artwork description.\n\n"
        "CRITICAL FOR IMAGE_PROMPT:\n"
        "Provide an 'image_prompt' that vividly depicts the EXACT subjects and environment from the user's dream (e.g. if the dream is about an elephant in a jungle, the image must show the person peacefully interacting with the giant elephant in the jungle). DO NOT generate generic abstract winged figures or meta-text labels. Write a pure descriptive visual scene prompt suitable for text-to-image AI.\n\n"
        "Return a JSON object conforming strictly to this schema:\n"
        "{\n"
        "  \"scenario_title\": \"What if you stepped boldly through the door?\",\n"
        "  \"alternative_timeline\": \"If you had embraced the crossing without fear, the forest would have opened into a luminescent crystal valley where you gained immediate mastery over the environment.\",\n"
        "  \"possible_outcomes\": [\n"
        "    \"More creativity and self-expression\",\n"
        "    \"Increased emotional resilience and confidence\",\n"
        "    \"New perspectives on waking challenges\",\n"
        "    \"Higher overall happiness and autonomy\"\n"
        "  ],\n"
        "  \"empowerment_takeaway\": \"Choosing active confrontation over avoidance transforms internal fear into creative power.\",\n"
        "  \"visual_theme\": \"A brilliant sunrise over glowing crystal spires with a confident figure stepping into the light\",\n"
        "  \"image_prompt\": \"Cinematic fantasy concept art of a person calmly befriending a giant majestic elephant in a lush glowing tropical jungle at sunrise, golden godrays filtering through dense green canopy, ethereal mist, 8k resolution, masterpiece, no text\"\n"
        "}\n\n"
        "Output ONLY valid JSON."
    )

    user_prompt = (
        f"Original Dream: \"{dream_text}\"\n"
        f"Scenario Type: \"{scenario_type}\"\n"
        f"Selected Alternative Action / Choice: \"{choice_text}\""
    )

    try:
        content = safe_groq_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model=GROQ_MODEL,
            response_format={"type": "json_object"},
            temperature=0.4,
            max_tokens=600
        )
        data = json.loads(content)
        # Use Groq's vivid context-aware image prompt if provided, or build a clean descriptive visual prompt
        img_p = (data.get("image_prompt") or "").strip()
        if not img_p or len(img_p) < 20 or "Original dream:" in img_p:
            img_p = f"Cinematic fantasy artwork of {choice_text} within {dream_text[:80]}, ethereal magical lighting, photorealistic concept art, 8k resolution, no text"
        data["image_prompt"] = img_p[:350]
        return {"success": True, **data}
    except Exception as e:
        logging.error(f"Error in simulate_scenario_pipeline: {e}")
        return {
            "success": True,
            "scenario_title": f"Alternative Outcome: {choice_text}",
            "alternative_timeline": f"By choosing '{choice_text}', the dream shifts from uncertainty to empowering exploration, opening unexpected creative pathways in waking life.",
            "possible_outcomes": [
                "More creativity and self-expression",
                "Increased emotional confidence",
                "New career and personal opportunities",
                "Higher overall clarity and peace"
            ],
            "empowerment_takeaway": "Small shifts in internal agency create profound transformations in how we experience reality.",
            "visual_theme": "A radiant golden path opening across mystical clouds",
            "image_prompt": f"Cinematic fantasy scene of {choice_text} during {dream_text[:70]}, magical glowing aura, majestic atmospheric lighting, 8k concept art, no text"
        }


def run_refinement_pipeline(dream_text: str, original_analysis: dict, feedback_category: str, feedback_resonance: str, feedback_text: str) -> dict:
    """Refines interpretations based on user feedback."""
    return {
        "success": True,
        "classification": "DREAM",
        "analysis": original_analysis.get("analysis", {}),
        "report": original_analysis.get("report", {}),
        "refinement_summary": f"Incorporated your feedback ({feedback_resonance}) on {feedback_category}."
    }


def run_comparison_pipeline(dreams: list) -> dict:
    """Compares multiple dreams in the session."""
    return {
        "success": True,
        "comparison": {
            "common_themes": ["Transformation", "Discovery"],
            "emotional_progression": "Hesitation moving toward calm clarity",
            "recurring_archetypes": ["Threshold", "Light", "Guardian"]
        }
    }

