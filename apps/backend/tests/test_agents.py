import unittest
import sys
import os
from unittest.mock import AsyncMock, patch

# Ensure backend directory is in sys.path
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from agents.conversation import conversation_agent
from agents.validator import validator_agent
from ai.key_manager import KeyManager
from memory.session_store import redis_store

class TestAgents(unittest.IsolatedAsyncioTestCase):
    async def asyncTearDown(self):
        await redis_store.close()

    def test_key_manager_rotation_and_cooldown(self):
        """Test API key round-robin selection and cooldown marking."""
        keys = ["key_A", "key_B"]
        km = KeyManager("TestProvider", keys)

        # First key selected has usage 0 -> key_A
        k1 = km.get_key()
        self.assertEqual(k1, "key_A")

        # Second key selected has lower usage (0) -> key_B
        k2 = km.get_key()
        self.assertEqual(k2, "key_B")

        # Mark key_A as exhausted
        km.mark_key_exhausted("key_A", cooldown_seconds=60)

        # Now only key_B should be active
        self.assertEqual(km.get_key(), "key_B")

    async def test_validator_agent_empty_data(self):
        """Test ValidatorAgent handling empty dataset gracefully."""
        input_data = {
            "cleaned_data": [],
            "extraction_goal": "Get products",
            "expected_fields": ["name", "price"]
        }
        res = await validator_agent.run(input_data, session_id="test_val_sess")
        val = res.get("validation")
        self.assertIsNotNone(val)
        self.assertEqual(val["confidence_score"], 0)
        self.assertFalse(val["is_valid"])

    @patch("agents.conversation.ai_router.generate")
    async def test_conversation_agent_hoisting_json_mode(self, mock_generate):
        """Test FIX 3: filtered_data and export_requested are hoisted to top-level in JSON mode."""
        mock_response = """```json
{
  "response_text": "Here are the top 2 items formatted as requested.",
  "filtered_data": [{"name": "Filtered Item 1", "price": 10}],
  "export_requested": "csv"
}
```"""
        mock_generate.return_value = mock_response

        input_data = {
            "user_request": "Show only items under $20 and export to csv",
            "cleaned_data": [
                {"name": "Filtered Item 1", "price": 10},
                {"name": "Expensive Item", "price": 100}
            ]
        }

        output = await conversation_agent.run(input_data, session_id="test_conv_hoist")
        self.assertIn("filtered_data", output)
        self.assertEqual(len(output["filtered_data"]), 1)
        self.assertEqual(output["filtered_data"][0]["name"], "Filtered Item 1")
        self.assertEqual(output.get("export_requested"), "csv")

    @patch("agents.conversation.ai_router.generate")
    async def test_conversation_agent_hoisting_fallback_mode(self, mock_generate):
        """Test FIX 3: In fallback (non-JSON) mode, filtered_data defaults to dataset and export_requested to none."""
        mock_generate.return_value = "I am a plain text response without JSON formatting."

        input_data = {
            "user_request": "What is the average price?",
            "cleaned_data": [{"name": "Item A", "price": 15}]
        }

        output = await conversation_agent.run(input_data, session_id="test_conv_fallback")
        self.assertIn("filtered_data", output)
        self.assertEqual(output["filtered_data"], input_data["cleaned_data"])
        self.assertEqual(output.get("export_requested"), "none")

if __name__ == "__main__":
    unittest.main()
