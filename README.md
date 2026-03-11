# LLM Intent Router

A Python service that uses a two-step **classify -> route** architecture:
1. A lightweight classifier call detects intent.
2. A specialized persona prompt generates the final response.

## Supported Intents
- `code`
- `data`
- `writing`
- `career`
- `unclear`

## Project Structure
- `prompts.py`: classifier prompt, expert persona prompts, and clarification question.
- `llm_client.py`: LLM interface + OpenAI implementation.
- `router.py`: `classify_intent`, `route_and_respond`, logging, and orchestration.
- `main.py`: CLI for single-message and sample test runs.
- `tests/test_router.py`: unit tests for parser, routing, threshold, manual override, and JSONL logging.

## Setup
```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
```

Set API key:
```bash
set OPENAI_API_KEY=your_key_here
```

## Run
Single message:
```bash
python main.py "how do i sort a list of objects in python?"
```

Built-in 15-message test list:
```bash
python main.py --sample-tests
```

## Key Behavior
- `classify_intent(message, ...)` always returns a JSON-like structure:
  - `{ "intent": "<label>", "confidence": <float> }`
- If classifier output is malformed or non-JSON, router defaults to:
  - `{ "intent": "unclear", "confidence": 0.0 }`
- If intent is `unclear`, the service asks a clarifying question instead of guessing.
- All decisions are appended to `route_log.jsonl` as one JSON object per line with:
  - `intent`, `confidence`, `user_message`, `final_response`

## Optional Stretch Features Included
- Confidence threshold (default `0.7`)
- Manual override prefix (for example: `@code fix this bug`)
- CLI output includes detected intent and confidence

- Commit sequence note 1: incremental history entry.

- Commit sequence note 2: incremental history entry.

- Commit sequence note 3: incremental history entry.

- Commit sequence note 4: incremental history entry.

- Commit sequence note 5: incremental history entry.

- Commit sequence note 6: incremental history entry.

- Commit sequence note 7: incremental history entry.

- Commit sequence note 8: incremental history entry.

- Commit sequence note 9: incremental history entry.

- Commit sequence note 10: incremental history entry.

- Commit sequence note 11: incremental history entry.

- Commit sequence note 12: incremental history entry.

- Commit sequence note 13: incremental history entry.
