"""Phase 2 validation: talk to a local llama_cpp.server via the OpenAI SDK."""

import argparse
import os
import time

from openai import OpenAI

DEFAULT_PROMPT = "Explain what a small language model is in two sentences."


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Send one chat completion to a local OpenAI-compatible server."
    )
    parser.add_argument(
        "--base-url",
        default=os.environ.get("LLM_BASE_URL", "http://127.0.0.1:8080/v1"),
        help="Base URL of the OpenAI-compatible server.",
    )
    parser.add_argument(
        "--prompt", default=DEFAULT_PROMPT, help="Prompt to send to the model."
    )
    parser.add_argument(
        "--max-tokens", type=int, default=128, help="Maximum tokens to generate."
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    client = OpenAI(base_url=args.base_url, api_key="dummy")

    print(f"Server: {args.base_url}")
    print(f"Prompt: {args.prompt!r}")

    start = time.perf_counter()
    response = client.chat.completions.create(
        model="local-model",
        messages=[{"role": "user", "content": args.prompt}],
        max_tokens=args.max_tokens,
    )
    elapsed = time.perf_counter() - start

    content = response.choices[0].message.content
    usage = response.usage

    print("\n--- Response ---")
    print(content)
    print("\n--- Metrics ---")
    print(f"Total time: {elapsed:.2f}s")
    if usage and usage.completion_tokens:
        print(f"Tokens:     {usage.completion_tokens}")
        print(f"Tokens/sec: {usage.completion_tokens / elapsed:.2f}")


if __name__ == "__main__":
    main()
