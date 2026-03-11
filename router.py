"""Intent classification and routing service."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from llm_client import LLMClient
from prompts import CLASSIFIER_SYSTEM_PROMPT, CLARIFYING_QUESTION, EXPERT_PROMPTS, INTENTS


@dataclass
class RouterConfig:
    classifier_model: str = "gpt-4o-mini"
    generation_model: str = "gpt-4o-mini"
    confidence_threshold: float = 0.7
    log_file: Path = Path("route_log.jsonl")


def _safe_default_intent() -> dict[str, Any]:
    return {"intent": "unclear", "confidence": 0.0}


def _normalize_intent(value: Any) -> str:
    intent = str(value).strip().lower()
    return intent if intent in INTENTS else "unclear"


def _normalize_confidence(value: Any) -> float:
    try:
        conf = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, conf))


def parse_classifier_response(raw_response: str) -> dict[str, Any]:
    """Parse classifier JSON output safely.

    Returns the default unclear intent when parsing fails.
    """
    try:
        data = json.loads(raw_response)
        if not isinstance(data, dict):
            return _safe_default_intent()
        intent = _normalize_intent(data.get("intent"))
        confidence = _normalize_confidence(data.get("confidence"))
        return {"intent": intent, "confidence": confidence}
    except (json.JSONDecodeError, TypeError):
        return _safe_default_intent()


def parse_manual_override(message: str) -> tuple[str | None, str]:
    """Support @intent prefix override, e.g. '@code help with this bug'."""
    match = re.match(r"^@(code|data|writing|career|unclear)\b\s*", message.strip(), re.IGNORECASE)
    if not match:
        return None, message

    intent = match.group(1).lower()
    stripped_message = message.strip()[match.end() :].strip()
    return intent, stripped_message


def classify_intent(message: str, llm: LLMClient, config: RouterConfig) -> dict[str, Any]:
    """Classify the user intent with a lightweight LLM call."""
    messages = [
        {"role": "system", "content": CLASSIFIER_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                "Classify this message and return only JSON with keys intent and confidence:\n"
                f"{message}"
            ),
        },
    ]

    raw = llm.chat(messages=messages, model=config.classifier_model)
    result = parse_classifier_response(raw)

    if result["confidence"] < config.confidence_threshold:
        return _safe_default_intent()

    return result


def route_and_respond(
    message: str,
    intent_payload: dict[str, Any],
    llm: LLMClient,
    config: RouterConfig,
) -> str:
    """Route to the selected expert persona or ask for clarification."""
    intent = _normalize_intent(intent_payload.get("intent"))
    if intent == "unclear":
        return CLARIFYING_QUESTION

    system_prompt = EXPERT_PROMPTS.get(intent)
    if not system_prompt:
        return CLARIFYING_QUESTION

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message},
    ]
    return llm.chat(messages=messages, model=config.generation_model).strip()


def log_route_decision(
    user_message: str,
    intent_payload: dict[str, Any],
    final_response: str,
    config: RouterConfig,
) -> None:
    entry = {
        "intent": _normalize_intent(intent_payload.get("intent")),
        "confidence": _normalize_confidence(intent_payload.get("confidence")),
        "user_message": user_message,
        "final_response": final_response,
    }

    config.log_file.parent.mkdir(parents=True, exist_ok=True)
    with config.log_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=True) + "\n")


def handle_message(message: str, llm: LLMClient, config: RouterConfig | None = None) -> dict[str, Any]:
    """Orchestrate override, classify, route, and logging for one user message."""
    config = config or RouterConfig()
    override_intent, normalized_message = parse_manual_override(message)

    if override_intent:
        intent_payload = {"intent": override_intent, "confidence": 1.0}
    else:
        intent_payload = classify_intent(normalized_message, llm, config)

    final_response = route_and_respond(normalized_message, intent_payload, llm, config)
    log_route_decision(message, intent_payload, final_response, config)

    return {
        "intent": _normalize_intent(intent_payload.get("intent")),
        "confidence": _normalize_confidence(intent_payload.get("confidence")),
        "final_response": final_response,
    }
