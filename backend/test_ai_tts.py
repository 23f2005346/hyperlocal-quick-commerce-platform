import os
import sys
import json
import base64
import unittest
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

from app import create_app, db, call_gemini_tts, Product

class TestAiVoiceTts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

    def test_call_gemini_tts_direct(self):
        """Verify Gemini 3.8 Flash-Lite TTS synthesizes Marathi speech"""
        text = "तुमची २ किलो साखर आणि १ किलो आटा जोडला आहे."
        ok, audio_b64, mime = call_gemini_tts(text, voice='Kore')
        self.assertTrue(ok, "TTS synthesis should succeed")
        self.assertIsNotNone(audio_b64, "Audio base64 should not be None")
        self.assertGreater(len(audio_b64), 1000, "Audio data should be substantive")
        self.assertEqual(mime, "audio/wav")

    def test_tts_api_endpoint(self):
        """Verify /api/ai/tts endpoint returns 200 with audio payload"""
        res = self.client.post('/api/ai/tts', json={
            'text': 'कोमल मार्टमध्ये आपले स्वागत आहे.',
            'voice': 'Kore'
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get('success'))
        self.assertIn('audio_base64', data)
        self.assertGreater(len(data['audio_base64']), 1000)

    def test_parse_order_with_tts_presynthesis(self):
        """Verify /api/ai/parse-order returns items and pre-synthesized audio"""
        res = self.client.post('/api/ai/parse-order', json={
            'text': '२ किलो साखर आणि ५०० ग्रॅम तूर डाळ',
            'language': 'mr'
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get('success'))
        self.assertGreaterEqual(len(data.get('items', [])), 2)
        # Verify TTS audio is pre-synthesized in response
        self.assertIsNotNone(data.get('audio_base64'), "Should return pre-synthesized TTS audio")
        self.assertEqual(data.get('audio_mime_type'), 'audio/wav')

if __name__ == '__main__':
    unittest.main()
