"""Real orchestrator-level tests (agents + Redis are stubbed; no network, no browser, no LLM)."""
import os, sys, unittest
from unittest.mock import patch

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import importlib

# NB: `from agents import orchestrator` would return the *instance* re-exported by agents/__init__.py, not the module
orch_mod = importlib.import_module("agents.orchestrator")


class FakeRedis:
    async def get_session_data(self, sid): return {}
    async def list_uploaded_context_ids(self, sid): return []
    async def get_uploaded_rows(self, sid, fid): return []
    async def get_uploaded_context(self, sid, fid): return ""
    async def set_pipeline_progress(self, sid, step): pass
    async def clear_pipeline_progress(self, sid): pass


class FakeAgent:
    def __init__(self, fn=None):
        self.calls = 0
        self.fn = fn or (lambda state: state)
    async def run(self, state, sid):
        self.calls += 1
        return self.fn(state)


def _build(browser_fn=None, extractor_rows=None):
    o = orch_mod.PipelineOrchestrator()
    o.planner = FakeAgent(lambda s: {**s, "extraction_goal": "x", "expected_fields": []})
    o.analyzer = FakeAgent(lambda s: {**s, "analysis": {"requires_js_rendering": True}})
    o.browser = FakeAgent(browser_fn or (lambda s: {**s, "dom_snapshots": ["<p>hi</p>"], "browse_stats": {"snapshots": 1, "chars": 9}}))
    o.extractor = FakeAgent(lambda s: {**s, "extracted_data": extractor_rows or []})
    o.cleaner = FakeAgent(lambda s: {**s, "cleaned_data": s.get("extracted_data", [])})
    o.validator = FakeAgent(lambda s: {**s, "validation": {"is_valid": bool(s.get("cleaned_data"))}})
    o.memory = FakeAgent()
    o.conversation = FakeAgent(lambda s: {**s, "conversation_response": {"response_text": "ok", "export_requested": "none", "result_count": 1}})
    o.exporter = FakeAgent()
    return o


class TestOrchestratorAccessFlow(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.p1 = patch.object(orch_mod, "redis_store", FakeRedis())
        self.p2 = patch.object(orch_mod, "validate_target_url", lambda u: True)
        self.p1.start(); self.p2.start()

    def tearDown(self):
        self.p1.stop(); self.p2.stop()

    async def run_url(self, o, url):
        res = await o.execute_pipeline("get data", url, "sess-12345678")
        return res["data"]["conversation_response"]["response_text"], res["data"]

    async def test_known_private_url_short_circuits_and_guides(self):
        o = _build()
        text, data = await self.run_url(o, "https://chatgpt.com/c/abc-123")
        self.assertEqual(o.analyzer.calls, 0)
        self.assertEqual(o.browser.calls, 0)
        self.assertEqual(o.extractor.calls, 0)
        self.assertIn("Share", text)
        self.assertEqual(data["url_access_issue"], "private_auth")

    async def test_bot_wall_message_is_specific(self):
        o = _build(browser_fn=lambda s: {**s, "dom_snapshots": [], "url_access_issue": "access_blocked", "browse_stats": {"snapshots": 0, "chars": 0}})
        text, _ = await self.run_url(o, "https://www.flipkart.com/q/lenovo-loq")
        self.assertIn("bot protection", text)
        self.assertNotIn("private", text.lower())

    async def test_loaded_but_nothing_found_does_not_blame_the_url(self):
        o = _build(extractor_rows=[])
        text, _ = await self.run_url(o, "https://www.amazon.in/s?k=laptop")
        self.assertIn("opened the page", text)

    async def test_nothing_loaded_and_no_classification(self):
        o = _build(browser_fn=lambda s: {**s, "dom_snapshots": [], "browse_stats": {"snapshots": 0, "chars": 0}})
        text, _ = await self.run_url(o, "https://example.org/x")
        self.assertIn("couldn't read any content", text)

    async def test_login_suspected_does_not_skip_extraction(self):
        o = _build(browser_fn=lambda s: {**s, "dom_snapshots": ["<li>a</li>"], "url_access_issue": "login_suspected",
                                         "browse_stats": {"snapshots": 1, "chars": 10}},
                   extractor_rows=[{"name": "A", "price": 1}])
        text, data = await self.run_url(o, "https://shop.example.com/list")
        self.assertEqual(o.extractor.calls, 1)
        self.assertEqual(text, "ok")           # normal conversation path = success preserved

    async def test_success_path_unchanged(self):
        o = _build(extractor_rows=[{"name": "A"}, {"name": "B"}])
        text, data = await self.run_url(o, "https://books.toscrape.com/")
        self.assertEqual(text, "ok")
        self.assertEqual(data["dataset_rows"], 2)
        self.assertEqual(o.conversation.calls, 1)


if __name__ == "__main__":
    unittest.main()
