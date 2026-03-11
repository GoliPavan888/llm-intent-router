"""CLI for the intent router service."""

from __future__ import annotations

import argparse
import os

from llm_client import OpenAILLMClient
from router import RouterConfig, handle_message

SAMPLE_MESSAGES = [
    "how do i sort a list of objects in python?",
    "explain this sql query for me",
    "This paragraph sounds awkward, can you help me fix it?",
    "I'm preparing for a job interview, any tips?",
    "what's the average of these numbers: 12, 45, 23, 67, 34",
    "Help me make this better.",
    "I need to write a function that takes a user id and returns their profile, but also i need help with my resume.",
    "hey",
    "Can you write me a poem about clouds?",
    "Rewrite this sentence to be more professional.",
    "I'm not sure what to do with my career.",
    "what is a pivot table",
    "fxi thsi bug pls: for i in range(10) print(i)",
    "How do I structure a cover letter?",
    "My boss says my writing is too verbose.",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="LLM intent router")
    parser.add_argument("message", nargs="?", help="Single message to route")
    parser.add_argument(
        "--sample-tests",
        action="store_true",
        help="Run the built-in sample messages (15 inputs)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.7,
        help="Classifier confidence threshold",
    )
    parser.add_argument(
        "--classifier-model",
        default="gpt-4o-mini",
        help="Model for intent classification",
    )
    parser.add_argument(
        "--generation-model",
        default="gpt-4o-mini",
        help="Model for persona response generation",
    )
    return parser


def process_message(message: str, client: OpenAILLMClient, config: RouterConfig) -> None:
    result = handle_message(message=message, llm=client, config=config)
    print("-" * 80)
    print(f"User Message: {message}")
    print(f"Detected Intent: {result['intent']}")
    print(f"Confidence: {result['confidence']:.2f}")
    print("Final Response:")
    print(result["final_response"])


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAILLMClient(api_key=api_key)

    config = RouterConfig(
        classifier_model=args.classifier_model,
        generation_model=args.generation_model,
        confidence_threshold=args.threshold,
    )

    if args.sample_tests:
        for message in SAMPLE_MESSAGES:
            process_message(message, client, config)
        return

    if args.message:
        process_message(args.message, client, config)
        return

    print("Enter a message (Ctrl+C to exit):")
    while True:
        user_message = input("> ").strip()
        if not user_message:
            continue
        process_message(user_message, client, config)


if __name__ == "__main__":
    main()
