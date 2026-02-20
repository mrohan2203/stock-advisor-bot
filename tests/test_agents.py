# tests/test_agents.py
import unittest
from agents.orchestrator import analyze_with_gpt

class TestAgentLogic(unittest.TestCase):
    def test_analysis_output(self):
        # We test if the agent returns a string (the report)
        response = analyze_with_gpt("TSLA")
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 50) # Ensure it's not an empty string

if __name__ == "__main__":
    unittest.main()