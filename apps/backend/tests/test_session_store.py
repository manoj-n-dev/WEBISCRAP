import unittest
import sys
import os
import uuid
import asyncio

# Ensure backend directory is in sys.path
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from memory.session_store import redis_store

class TestSessionStore(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        await redis_store.connect()
        self.test_session_id = f"test_session_{uuid.uuid4().hex[:8]}"
        self.test_user_id = f"test_user_{uuid.uuid4().hex[:8]}"

    async def asyncTearDown(self):
        # Clean up test keys
        await redis_store.delete(
            f"session:{self.test_session_id}:data",
            f"session:{self.test_session_id}:owner",
            f"session:{self.test_session_id}:history",
            f"pipeline_progress:{self.test_session_id}",
            f"user_sessions:{self.test_user_id}"
        )
        await redis_store.close()

    async def test_session_data_lifecycle(self):
        """Test saving and retrieving session data."""
        payload = {"status": "success", "count": 42, "items": [{"name": "item1"}]}
        await redis_store.save_session_data(self.test_session_id, payload, ttl_seconds=60)

        retrieved = await redis_store.get_session_data(self.test_session_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["status"], "success")
        self.assertEqual(retrieved["count"], 42)
        self.assertEqual(len(retrieved["items"]), 1)

    async def test_session_owner_lifecycle(self):
        """Test setting and getting session owner."""
        await redis_store.set_session_owner(self.test_session_id, self.test_user_id, ttl_seconds=60)
        owner = await redis_store.get_session_owner(self.test_session_id)
        self.assertEqual(owner, self.test_user_id)

    async def test_conversation_history(self):
        """Test appending and retrieving conversation history."""
        msg1 = {"role": "user", "content": "Extract phones from xyz"}
        msg2 = {"role": "assistant", "content": "Extracted 5 phones."}

        await redis_store.append_conversation_history(self.test_session_id, msg1)
        await redis_store.append_conversation_history(self.test_session_id, msg2)

        history = await redis_store.get_conversation_history(self.test_session_id)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["content"], "Extract phones from xyz")
        self.assertEqual(history[1]["content"], "Extracted 5 phones.")

    async def test_pipeline_progress_tracking(self):
        """Test FIX 1: set_pipeline_progress, get_pipeline_progress, clear_pipeline_progress."""
        # Initial should be None
        initial = await redis_store.get_pipeline_progress(self.test_session_id)
        self.assertIsNone(initial)

        # Set step
        await redis_store.set_pipeline_progress(self.test_session_id, "browse", ttl_seconds=60)
        step = await redis_store.get_pipeline_progress(self.test_session_id)
        self.assertEqual(step, "browse")

        # Update step
        await redis_store.set_pipeline_progress(self.test_session_id, "extract", ttl_seconds=60)
        step = await redis_store.get_pipeline_progress(self.test_session_id)
        self.assertEqual(step, "extract")

        # Clear step
        await redis_store.clear_pipeline_progress(self.test_session_id)
        cleared = await redis_store.get_pipeline_progress(self.test_session_id)
        self.assertIsNone(cleared)

    async def test_jti_blacklisting(self):
        """Test FIX 1 & 6: blacklist_jti and is_jti_blacklisted."""
        test_jti = str(uuid.uuid4())
        self.assertFalse(await redis_store.is_jti_blacklisted(test_jti))

        await redis_store.blacklist_jti(test_jti, expiry_seconds=60)
        self.assertTrue(await redis_store.is_jti_blacklisted(test_jti))

        # Cleanup
        await redis_store.delete(f"blacklist:jti:{test_jti}")

    async def test_user_session_tracking_order(self):
        """Test FIX 2: add_user_session and get_user_sessions (sorted by recency)."""
        sess1 = f"sess_{uuid.uuid4().hex[:6]}"
        sess2 = f"sess_{uuid.uuid4().hex[:6]}"
        sess3 = f"sess_{uuid.uuid4().hex[:6]}"

        await redis_store.add_user_session(self.test_user_id, sess1, ttl_seconds=60)
        await asyncio.sleep(0.05)
        await redis_store.add_user_session(self.test_user_id, sess2, ttl_seconds=60)
        await asyncio.sleep(0.05)
        await redis_store.add_user_session(self.test_user_id, sess3, ttl_seconds=60)

        sessions = await redis_store.get_user_sessions(self.test_user_id)
        # Most recent session first: sess3, sess2, sess1
        self.assertIn(sess1, sessions)
        self.assertIn(sess2, sessions)
        self.assertIn(sess3, sessions)
        self.assertEqual(sessions[0], sess3)
        self.assertEqual(sessions[1], sess2)
        self.assertEqual(sessions[2], sess1)

    async def test_uploaded_context_tracking(self):
        """Test FIX 13: save_uploaded_context and get_uploaded_context."""
        file_id = f"file_{uuid.uuid4().hex[:6]}"
        sample_text = "Extracted PDF content with product table and prices."

        await redis_store.save_uploaded_context(self.test_session_id, file_id, sample_text, ttl_seconds=60)
        retrieved = await redis_store.get_uploaded_context(self.test_session_id, file_id)
        self.assertEqual(retrieved, sample_text)

        # Cleanup
        await redis_store.delete(
            f"uploaded_context:{self.test_session_id}:{file_id}",
            f"session_uploads:{self.test_session_id}"
        )

if __name__ == "__main__":
    unittest.main()
