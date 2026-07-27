import unittest
from unittest.mock import patch, MagicMock
import json

from services.input_classifier import classify_input
from services.pipeline import run_dream_pipeline, run_comparison_pipeline, run_refinement_pipeline

class TestDreamIntelligencePipeline(unittest.TestCase):

    def test_local_non_dream_heuristics(self):
        """Assert that standard non-dream inputs are immediately classified locally as NON_DREAM."""
        non_dreams = [
            "What is 2+3?",
            "Explain Python.",
            "Write a poem.",
            "What is the weather"
        ]
        for query in non_dreams:
            res = classify_input(query)
            self.assertEqual(res["classification"], "NON_DREAM")
            self.assertEqual(res["confidence"], 1.0)

    @patch('services.input_classifier._client')
    @patch('services.input_classifier.GROQ_API_KEY', 'mock_key')
    def test_mocked_classification_non_dream(self, mock_client_func):
        """Assert that an external non-dream query is validated as NON_DREAM and stops pipeline execution."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "classification": "NON_DREAM",
            "reasoning": "General knowledge query.",
            "confidence": 0.95
        })
        mock_client_func.return_value.chat.completions.create.return_value = mock_response

        # Verify raw classifier
        res = classify_input("Help me write a resume.")
        self.assertEqual(res["classification"], "NON_DREAM")
        
        # Verify pipeline exits early and does not call interpret stages
        pipeline_res = run_dream_pipeline("Help me write a resume.")
        self.assertEqual(pipeline_res["success"], True)
        self.assertEqual(pipeline_res["classification"], "NON_DREAM")
        self.assertIn("message", pipeline_res)
        self.assertNotIn("analysis", pipeline_res)

    @patch('services.input_classifier._client')
    @patch('services.input_classifier.GROQ_API_KEY', 'mock_key')
    def test_mocked_classification_ambiguous(self, mock_client_func):
        """Assert that ambiguous single word inputs prompt for context."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "classification": "AMBIGUOUS",
            "reasoning": "Single symbol provided.",
            "confidence": 0.9
        })
        mock_client_func.return_value.chat.completions.create.return_value = mock_response

        pipeline_res = run_dream_pipeline("Snake")
        self.assertEqual(pipeline_res["success"], True)
        self.assertEqual(pipeline_res["classification"], "AMBIGUOUS")
        self.assertIn("message", pipeline_res)
        self.assertNotIn("analysis", pipeline_res)

    @patch('services.pipeline.classify_input')
    @patch('services.pipeline.decompose_dream')
    @patch('services.pipeline.analyze_emotions')
    @patch('services.pipeline.analyze_symbols')
    @patch('services.pipeline.analyze_narrative')
    @patch('services.pipeline.detect_conflicts')
    @patch('services.pipeline.generate_interpretations')
    @patch('services.pipeline.synthesize_report')
    def test_mocked_dream_pipeline(self, mock_synth, mock_gen, mock_conf, mock_nar, mock_sym, mock_emo, mock_dec, mock_class):
        """Assert that a valid dream text runs through all stages and merges successfully."""
        mock_class.return_value = {"classification": "DREAM", "confidence": 1.0}
        mock_dec.return_value = {"setting": ["house"], "beginning_state": "in a hallway"}
        mock_emo.return_value = {"dominant_emotion": "anxiety", "stages": []}
        mock_sym.return_value = [{"symbol": "door", "associated_emotion": "urgency"}]
        mock_nar.return_value = {"protagonist_role": "running"}
        mock_conf.return_value = {"conflicts": [], "conflict_matrix": {"quadrant": "AVOIDANCE"}}
        mock_gen.return_value = {
            "hypotheses": [{"title": "Avoidance", "confidence": "High"}],
            "turning_point_simulation": {"turning_point_description": "hallway"}
        }
        mock_synth.return_value = {
            "atmosphere": "tense",
            "what_mind_exploring": "exploring escape",
            "uncertainty_note": "Exploratory"
        }

        pipeline_res = run_dream_pipeline("I dreamed I was running down a hallway and saw a door.")
        
        self.assertEqual(pipeline_res["success"], True)
        self.assertEqual(pipeline_res["classification"], "DREAM")
        self.assertIn("analysis", pipeline_res)
        
        analysis = pipeline_res["analysis"]
        self.assertEqual(analysis["decomposition"]["beginning_state"], "in a hallway")
        self.assertEqual(analysis["emotions"]["dominant_emotion"], "anxiety")
        self.assertEqual(analysis["symbols"][0]["symbol"], "door")
        self.assertEqual(analysis["narrative"]["protagonist_role"], "running")
        self.assertEqual(analysis["conflict_matrix"]["quadrant"], "AVOIDANCE")
        self.assertEqual(analysis["hypotheses"][0]["title"], "Avoidance")
        self.assertEqual(analysis["turning_point"]["turning_point_description"], "hallway")
        
        self.assertEqual(pipeline_res["report"]["atmosphere"], "tense")
        self.assertEqual(len(pipeline_res["processing_stages"]), 8)

    @patch('services.pipeline._client')
    @patch('services.pipeline.GROQ_API_KEY', 'mock_key')
    def test_comparison_structure(self, mock_client_func):
        """Assert that comparing dreams compiles correctly with structured metrics."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "comparison": {
                "shared_symbols": "Rising water connects both.",
                "emotional_differences": "Dream A had fear, Dream B had relief.",
                "narrative_structure": "Transition from enclosed spaces to open water.",
                "dreamer_actions": "Moving away in A, swimming in B.",
                "conflicts": "Avoidance vs confrontation.",
                "endings": "Unresolved in A, resolved in B."
            },
            "recurring_patterns": "Across this current session, the dreams share a recurring narrative pattern.",
            "personal_growth_insight": "Reflects progressive emotional processing."
        })
        mock_client_func.return_value.chat.completions.create.return_value = mock_response

        dreams = [
            {"dream_text": "I was stuck in a flooding basement.", "analysis": {}},
            {"dream_text": "I was swimming in a clear lake.", "analysis": {}}
        ]
        
        res = run_comparison_pipeline(dreams)
        self.assertIn("comparison", res)
        self.assertEqual(res["comparison"]["shared_symbols"], "Rising water connects both.")
        self.assertEqual(res["comparison"]["endings"], "Unresolved in A, resolved in B.")
        self.assertIn("recurring_patterns", res)

if __name__ == '__main__':
    unittest.main()
