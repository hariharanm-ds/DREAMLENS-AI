import json
import logging
from concurrent.futures import ThreadPoolExecutor
from groq_client import _client, GROQ_API_KEY, GROQ_MODEL
from services.input_classifier import classify_input
from services.dream_decomposer import decompose_dream
from services.emotion_analyzer import analyze_emotions
from services.symbol_analyzer import analyze_symbols
from services.narrative_analyzer import analyze_narrative
from services.conflict_detector import detect_conflicts
from services.interpretation_engine import generate_interpretations, refine_interpretation
from services.report_synthesizer import synthesize_report

def run_dream_pipeline(dream_text: str) -> dict:
    """
    Runs the entire multi-stage Dream Intelligence Pipeline.
    1. Classifies input.
    2. If DREAM, runs extraction stages in parallel.
    3. Runs interpretation generator.
    4. Runs report synthesizer.
    """
    logging.info(f"DreamLens Pipeline started for text length {len(dream_text or '')}")
    
    # 1. Classification
    classification_result = classify_input(dream_text)
    classification = classification_result.get("classification", "DREAM")
    
    logging.info(f"Input classification: {classification} (confidence: {classification_result.get('confidence')})")
    
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
        
    # 2. Parallel Feature Extraction
    extracted_data = {}
    
    # Run the 5 extraction stages concurrently
    try:
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_decomp = executor.submit(decompose_dream, dream_text)
            
            # Wait for decomposition first as it can optionally feed into other analyzers
            # but to run in parallel, we can feed the raw text to all and merge them.
            # To be safe, we run all with raw text in parallel.
            future_emotions = executor.submit(analyze_emotions, dream_text)
            future_symbols = executor.submit(analyze_symbols, dream_text)
            future_narrative = executor.submit(analyze_narrative, dream_text)
            future_conflicts = executor.submit(detect_conflicts, dream_text)
            
            # Gather results
            decomp = future_decomp.result()
            emotions = future_emotions.result()
            symbols = future_symbols.result()
            narrative = future_narrative.result()
            conflicts = future_conflicts.result()
            
            extracted_data = {
                "decomposition": decomp,
                "emotions": emotions,
                "symbols": symbols,
                "narrative": narrative,
                "conflicts": conflicts.get("conflicts", []),
                "conflict_matrix": conflicts.get("conflict_matrix", {})
            }
    except Exception as e:
        logging.error(f"Error in parallel pipeline extraction: {e}")
        # Build standard fallbacks
        extracted_data = {
            "decomposition": decompose_dream(dream_text),
            "emotions": analyze_emotions(dream_text),
            "symbols": analyze_symbols(dream_text),
            "narrative": analyze_narrative(dream_text),
            "conflicts": [],
            "conflict_matrix": {}
        }
        
    # 3. Interpretation & Hypotheses
    logging.info("Generating hypotheses...")
    interpretations = generate_interpretations(dream_text, extracted_data)
    
    # 4. Synthesize final report
    logging.info("Synthesizing final report...")
    report = synthesize_report(dream_text, extracted_data, interpretations)
    
    return {
        "success": True,
        "classification": "DREAM",
        "analysis": {
            "decomposition": extracted_data["decomposition"],
            "emotions": extracted_data["emotions"],
            "symbols": extracted_data["symbols"],
            "narrative": extracted_data["narrative"],
            "conflicts": extracted_data["conflicts"],
            "conflict_matrix": extracted_data["conflict_matrix"],
            "hypotheses": interpretations.get("hypotheses", []),
            "turning_point": interpretations.get("turning_point_simulation", {})
        },
        "report": report,
        "processing_stages": [
            "input_classifier",
            "dream_decomposer",
            "emotion_analyzer",
            "symbol_analyzer",
            "narrative_analyzer",
            "conflict_detector",
            "interpretation_engine",
            "report_synthesizer"
        ]
    }


def run_refinement_pipeline(dream_text: str, original_analysis: dict, feedback_category: str, feedback_resonance: str, feedback_text: str) -> dict:
    """
    Refines interpretations based on user feedback.
    """
    refined_data = refine_interpretation(dream_text, original_analysis, feedback_category, feedback_resonance, feedback_text)
    
    # Merge refined analysis with original analysis
    updated_analysis = original_analysis.copy()
    if "analysis" in updated_analysis:
        if "hypotheses" in updated_analysis["analysis"] and "refined_hypotheses" in refined_data:
            updated_analysis["analysis"]["hypotheses"] = refined_data["refined_hypotheses"]
            
    updated_report = original_analysis.get("report", {}).copy()
    refined_report_data = refined_data.get("refined_report", {})
    for key, val in refined_report_data.items():
        updated_report[key] = val
        
    return {
        "success": True,
        "classification": "DREAM",
        "analysis": updated_analysis.get("analysis", {}),
        "report": updated_report,
        "refinement_summary": refined_data.get("refinement_summary", "Interpretations updated successfully.")
    }


def run_comparison_pipeline(dreams: list) -> dict:
    """
    Compares two or more dreams in the session.
    Expects dreams: [{"dream_text": "...", "analysis": {...}}]
    """
    default_compare = {
        "comparison": {
            "shared_symbols": "No shared symbols identified.",
            "emotional_differences": "Arcs differ slightly.",
            "narrative_structure": "Similar journey progressions.",
            "dreamer_actions": "Actions differ.",
            "conflicts": "Tensions differ.",
            "endings": "Varying resolutions."
        },
        "recurring_patterns": "Across this current session, the dreams reflect a sequence of processing general thoughts.",
        "personal_growth_insight": "A supportive reflection."
    }

    if not GROQ_API_KEY:
        return default_compare

    # Format dreams for the prompt
    dreams_data = []
    for idx, d in enumerate(dreams):
        dream_info = {
            "id": idx + 1,
            "dream_text": d.get("dream_text"),
            "emotions": d.get("analysis", {}).get("emotions", {}),
            "symbols": [s.get("symbol") for s in d.get("analysis", {}).get("symbols", []) if isinstance(s, dict)],
            "protagonist_role": d.get("analysis", {}).get("narrative", {}).get("protagonist_role", ""),
            "ending": d.get("analysis", {}).get("narrative", {}).get("ending", "")
        }
        dreams_data.append(dream_info)

    system_prompt = (
        "You are an expert dream intelligence system. You are comparing two or more dreams from the user's current session or local history.\n"
        "Your task is to identify links, comparisons, progressions, or recurring patterns.\n"
        "Crucial Guidance:\n"
        "- Adopt a highly supportive, wise, and exploratory tone.\n"
        "- Identify recurring patterns (e.g. 'Across this current session, the dreams share a recurring narrative pattern involving restricted movement and searching for an exit.').\n"
        "- Never claim diagnoses or supernatural messages.\n\n"
        "Return a JSON object conforming exactly to this schema:\n"
        "{\n"
        "  \"comparison\": {\n"
        "    \"shared_symbols\": \"Analysis of symbols that appear in multiple dreams or share common themes\",\n"
        "    \"emotional_differences\": \"Compare the emotional arcs, intensities, and dominant feelings\",\n"
        "    \"narrative_structure\": \"Compare the progression, actions, and narrative style\",\n"
        "    \"dreamer_actions\": \"Compare how the dreamer behaves (e.g. running vs confronting)\",\n"
        "    \"conflicts\": \"Compare the central tensions or contradictions\",\n"
        "    \"endings\": \"Compare how each dream resolves or ends\"\n"
        "  },\n"
        "  \"recurring_patterns\": \"Synthesized statement of patterns across the session thread (e.g. Across this current session, the dreams share a recurring narrative pattern involving...)\",\n"
        "  \"personal_growth_insight\": \"A supportive, open-ended growth insight regarding these comparisons\"\n"
        "}\n\n"
        "Output ONLY valid JSON."
    )

    try:
        client = _client()
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Dreams to compare: {json.dumps(dreams_data)}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=600
        )
        content = (response.choices[0].message.content or "").strip()
        data = json.loads(content)
        return data
    except Exception as e:
        logging.error(f"Error in comparison pipeline: {e}")
        return default_compare
