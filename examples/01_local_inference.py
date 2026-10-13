"""Phase 1 validation: load a GGUF model with llama-cpp-python and run one prompt."""

import argparse
import os
import sys

from slm_cpu_serving.metrics import run_inference

DEFAULT_PROMPT = "Explain what a small language model is in two sentences."


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run one inference pass against a local GGUF model."
    )
    parser.add_argument(
        "--model-path",
        default=os.environ.get("MODEL_PATH"),
        help="Path to a GGUF model file. Defaults to the MODEL_PATH environment variable.",
    )
    parser.add_argument(
        "--prompt", default=DEFAULT_PROMPT, help="Prompt to send to the model."
    )
    parser.add_argument(
        "--max-tokens", type=int, default=128, help="Maximum tokens to generate."
    )
    parser.add_argument(
        "--n-threads", type=int, default=os.cpu_count(), help="CPU threads to use."
    )
    parser.add_argument("--n-ctx", type=int, default=2048, help="Context window size.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not args.model_path:
        print(
            "Error: no model path provided. Set MODEL_PATH or pass --model-path.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Loading model: {args.model_path}")
    print(f"Prompt: {args.prompt!r}")
    result = run_inference(
        args.model_path,
        args.prompt,
        n_ctx=args.n_ctx,
        n_threads=args.n_threads,
        max_tokens=args.max_tokens,
    )

    print("\n--- Response ---")
    print(result.response)
    print("\n--- Metrics ---")
    print(f"Load time:           {result.load_time:.2f}s")
    print(f"Total time:          {result.total_time:.2f}s")
    if result.first_token_latency is not None:
        print(f"First-token latency: {result.first_token_latency:.2f}s")
    if result.tokens:
        print(f"Tokens:              {result.tokens}")
        print(f"Tokens/sec:          {result.tokens_per_sec:.2f}")
    else:
        print("Tokens/sec:          unavailable (no tokens generated)")
    print(f"Peak RAM:            {result.peak_rss_bytes / (1024**2):.1f} MB")
    print(
        f"CPU usage:           {result.cpu_percent:.1f}% (n_threads={args.n_threads})"
    )


if __name__ == "__main__":
    main()
