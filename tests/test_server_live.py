import unittest
import sys
sys.stdout.reconfigure(encoding='utf-8')
from app import app
import json

class TestDreamLensApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()

    def test_routes_exist(self):
        # 1. Landing page
        r = self.client.get('/')
        self.assertEqual(r.status_code, 200)
        self.assertIn(b'DREAMLENS', r.data)

        # 2. Chat interface
        r = self.client.get('/chat')
        self.assertEqual(r.status_code, 200)
        self.assertIn(b'DREAMLENS AI', r.data)

        # 3. Static assets
        for asset in ['dream_stage1.jpg', 'dream_stage2.jpg', 'dream_stage3.jpg', 'dream_stage4.jpg', 'dream_scenario.jpg', 'hero_dreamscape.jpg']:
            r = self.client.get(f'/static/{asset}')
            self.assertEqual(r.status_code, 200, f"Static asset {asset} missing!")
            self.assertGreater(len(r.data), 1000)

    def test_analyze_endpoint(self):
        payload = {
            "dream_text": "I was flying over glowing crystal mountains and a golden lion was waiting at the summit"
        }
        r = self.client.post('/api/dream/analyze', json=payload)
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertTrue(data.get('success'))
        self.assertEqual(data.get('classification'), 'DREAM')
        self.assertIn('in_short', data)
        self.assertIn('dream_profile', data)
        self.assertIn('story_timeline', data)
        self.assertIn('psychology', data)
        self.assertIn('symbol_network', data)
        self.assertIn('emotion_arc', data)
        print("Analyze test passed! In short summary:", data['in_short'].get('summary'))

    def test_scenario_endpoint(self):
        payload = {
            "dream_text": "I was chased by an elephant in the jungle",
            "choice_text": "I turn around, calm the elephant with peace and touch its forehead"
        }
        r = self.client.post('/api/dream/simulate_scenario', json=payload)
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertTrue(data.get('success'))
        self.assertIn('alternative_timeline', data)
        print("Scenario test passed! Title:", data.get('scenario_title'))

if __name__ == '__main__':
    unittest.main()
