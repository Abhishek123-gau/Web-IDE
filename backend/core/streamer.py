import sys
import re
from typing import Any


def _extract_final_answer(full_text: str) -> str:
    """
    DeepSeek R1 wraps its reasoning in <think>...</think> tags.
    This strips those out and returns only the final answer after </think>.
    If no <think> tag is found, returns the full text as-is.
    """
    # Check if there's a </think> tag
    if "</think>" in full_text:
        # Everything after </think> is the actual answer
        final = full_text.split("</think>")[-1].strip()
        return final if final else full_text.strip()
    # No think tag — return everything
    return full_text.strip()


def stream_llm(chain, inputs: dict, label: str = "LLM") -> str:
    """
    Streams tokens from a Langchain chain to the terminal in real-time.
    Automatically strips DeepSeek R1 <think> reasoning blocks from the
    returned string (they are still shown to the terminal for transparency).
    Returns the final clean response (after </think> if present).
    """
    print(f"\n\033[90m💬 [{label}] STREAMING RESPONSE:\033[0m")
    print("\033[90m" + "-" * 50 + "\033[0m")

    full_content = ""
    in_think_block = False

    try:
        for chunk in chain.stream(inputs):
            token = ""
            if hasattr(chunk, "content"):
                token = chunk.content
            elif isinstance(chunk, str):
                token = chunk

            full_content += token

            # Detect entering/exiting think block
            if "<think>" in full_content and not in_think_block:
                in_think_block = True

            if "</think>" in full_content and in_think_block:
                in_think_block = False

            # Show thinking tokens dimmed in grey, final output bright
            if in_think_block or "<think>" in token:
                sys.stdout.write(f"\033[90m{token}\033[0m")  # dim grey
            else:
                sys.stdout.write(f"\033[97m{token}\033[0m")  # bright white
            sys.stdout.flush()

    except Exception as e:
        print(f"\n[STREAM ERROR]: {e}")
        raise

    print("\n" + "-" * 50)

    # Return ONLY the final answer text (strip <think> block)
    final_answer = _extract_final_answer(full_content)
    return final_answer


def stream_llm_json(chain, inputs: dict, label: str = "LLM") -> Any:
    """
    Streams a JSON-producing LLM chain to the terminal.
    
    IMPORTANT: This function streams using the raw LLM (NOT through JsonOutputParser),
    to avoid DeepSeek R1's <think> tokens corrupting incremental JSON parsing.
    It then:
    1. Shows think tokens dimmed to the terminal
    2. Extracts the JSON block from the final output using regex
    3. Parses and returns the JSON dict
    """
    import json
    print(f"\n\033[90m💬 [{label}] STREAMING JSON RESPONSE:\033[0m")
    print("\033[90m" + "-" * 50 + "\033[0m")

    full_content = ""
    in_think_block = False

    # We need the raw LLM chain WITHOUT the parser to stream text tokens
    # The caller passes the full chain (LLM | Parser), so we re-invoke differently:
    # We stream raw text from the chain directly (before parser applies)
    try:
        for chunk in chain.stream(inputs):
            # JsonOutputParser yields dicts, but we need raw text here
            # If a dict comes through, we already have the final result
            if isinstance(chunk, dict):
                # JsonOutputParser finished - show and return
                raw_display = json.dumps(chunk, indent=None)
                sys.stdout.write(f"\r\033[K\033[92m✅ Final JSON: {raw_display[:120]}\033[0m")
                sys.stdout.flush()
                full_content = json.dumps(chunk)  # Store as string for extraction
                print("\n" + "-" * 50)
                return chunk  # Return the fully-parsed dict directly

            # Otherwise, it's a raw text token (pre-parser)
            token = ""
            if hasattr(chunk, "content"):
                token = chunk.content
            elif isinstance(chunk, str):
                token = chunk

            full_content += token

            # Track think block state
            if "<think>" in token:
                in_think_block = True
            if "</think>" in token:
                in_think_block = False

            if in_think_block or "<think>" in token:
                sys.stdout.write(f"\033[90m{token}\033[0m")  # dim grey for reasoning
            else:
                sys.stdout.write(f"\033[97m{token}\033[0m")  # bright white for JSON
            sys.stdout.flush()

    except Exception as e:
        print(f"\n[STREAM JSON ERROR]: {e}")
        raise

    print("\n" + "-" * 50)

    # Strip think block and parse JSON from remaining text
    clean_text = _extract_final_answer(full_content)

    # Extract JSON block using regex (handles ```json ... ``` or raw JSON)
    json_match = re.search(r"```(?:json)?\s*([\s\S]+?)```", clean_text)
    if json_match:
        clean_text = json_match.group(1).strip()
    else:
        # Try to find raw JSON object
        json_match = re.search(r"(\{[\s\S]+\})", clean_text)
        if json_match:
            clean_text = json_match.group(1).strip()

    try:
        result = json.loads(clean_text)
        print(f"\033[92m✅ [{label}] JSON parsed successfully\033[0m")
        return result
    except json.JSONDecodeError as e:
        print(f"\033[91m[JSON PARSE ERROR]: {e}\nRaw text was:\n{clean_text[:300]}\033[0m")
        return None
