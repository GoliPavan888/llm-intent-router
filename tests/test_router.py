"""Unit tests for routing logic using a fake LLM client."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from router import (
    RouterConfig,
    classify_intent,
    handle_message,
    parse_classifier_response,
    parse_manual_override,
    route_and_respond,
)


class FakeLLM:
    def __init__(self, responses: list[str]) -> None:
        self.responses = responses
        self.calls = []

    def chat(self, messages, model: str) -> str:
        self.calls.append({"messages": messages, "model": model})
        if not self.responses:
            return ""
        return self.responses.pop(0)


class RouterTests(unittest.TestCase):
    def test_parse_classifier_response_valid(self) -> None:
        parsed = parse_classifier_response('{"intent": "code", "confidence": 0.92}')
        self.assertEqual(parsed["intent"], "code")
        self.assertEqual(parsed["confidence"], 0.92)

    def test_parse_classifier_response_malformed_defaults_unclear(self) -> None:
        parsed = parse_classifier_response("not-json")
        self.assertEqual(parsed, {"intent": "unclear", "confidence": 0.0})

    def test_classify_intent_applies_threshold(self) -> None:
        llm = FakeLLM(['{"intent": "writing", "confidence": 0.4}'])
        cfg = RouterConfig(confidence_threshold=0.7)
        result = classify_intent("help me", llm, cfg)
        self.assertEqual(result, {"intent": "unclear", "confidence": 0.0})

    def test_route_unclear_asks_question(self) -> None:
        llm = FakeLLM([])
        response = route_and_respond("hello", {"intent": "unclear", "confidence": 0.0}, llm, RouterConfig())
        self.assertTrue(response.endswith("career advice?"))

    def test_manual_override(self) -> None:
        intent, msg = parse_manual_override("@code fix this please")
        self.assertEqual(intent, "code")
        self.assertEqual(msg, "fix this please")

    def test_handle_message_logs_jsonl(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            log_path = Path(tmp) / "route_log.jsonl"
            cfg = RouterConfig(log_file=log_path)
            llm = FakeLLM([
                '{"intent": "code", "confidence": 0.95}',
                "Use sorted(items, key=lambda x: x['id'])",
            ])
            result = handle_message("sort by id", llm, cfg)
            self.assertEqual(result["intent"], "code")
            self.assertTrue(log_path.exists())

            lines = log_path.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 1)
            payload = json.loads(lines[0])
            self.assertIn("intent", payload)
            self.assertIn("confidence", payload)
            self.assertIn("user_message", payload)
            self.assertIn("final_response", payload)


if __name__ == "__main__":
    unittest.main()
