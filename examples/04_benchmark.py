"""Phase 3 benchmarking: sweep thread counts, context sizes, and model files.

Writes one CSV row per (model, n_threads, n_ctx) combination so results are
easy to drop into a spreadsheet or discuss in class.
"""

import argparse
import csv
import os
import sys
from pathlib import Path

from slm_cpu_serving.metrics import run_inference

DEFAULT_PROMPT = "Explain what a small language model is in two sentences."

CSV_FIELDS = [
    "model",
    "n_threads",
    "n_ctx",
    "load_time_s",
    "first_token_latency_s",
    "total_time_s",
    "tokens",
    "tokens_per_sec",
    "peak_ram_mb",
    "cpu_percent",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Benchmark inference across thread counts, context sizes, and models."
    )
    parser.add_argument(
        "--model-path",
        nargs="+",
        required=True,
        help="One or more GGUF model files to benchmark (e.g. different sizes/quant levels).",
    )
    parser.add_argument(
        "--n-threads",
        type=int,
        nargs="+",
        default=[os.cpu_count()],
        help="Thread counts to sweep.",
    )
    parser.add_argument(
        "--n-ctx",
        type=int,
        nargs="+",
        default=[2048],
        help="Context window sizes to sweep.",
    )
    parser.add_argument(
        "--prompt", default=DEFAULT_PROMPT, help="Prompt to send to the model."
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=128,
        help="Maximum tokens to generate per run.",
    )
    parser.add_argument(
        "--repeats", type=int, default=1, help="Number of repeats per combination."
    )
    parser.add_argument(
        "--output",
        default="benchmark_results.csv",
        help="Path to write the CSV results.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    for model_path in args.model_path:
        if not Path(model_path).is_file():
            print(f"Error: model file not found: {model_path}", file=sys.stderr)
            sys.exit(1)

    combinations = [
        (model_path, n_threads, n_ctx)
        for model_path in args.model_path
        for n_threads in args.n_threads
        for n_ctx in args.n_ctx
        for _ in range(args.repeats)
    ]

    print(f"Running {len(combinations)} benchmark combination(s)...")

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()

        for i, (model_path, n_threads, n_ctx) in enumerate(combinations, start=1):
            print(
                f"[{i}/{len(combinations)}] model={model_path} "
                f"n_threads={n_threads} n_ctx={n_ctx}"
            )
            result = run_inference(
                model_path,
                args.prompt,
                n_ctx=n_ctx,
                n_threads=n_threads,
                max_tokens=args.max_tokens,
            )
            writer.writerow(
                {
                    "model": Path(model_path).name,
                    "n_threads": n_threads,
                    "n_ctx": n_ctx,
                    "load_time_s": f"{result.load_time:.3f}",
                    "first_token_latency_s": (
                        f"{result.first_token_latency:.3f}"
                        if result.first_token_latency is not None
                        else ""
                    ),
                    "total_time_s": f"{result.total_time:.3f}",
                    "tokens": result.tokens,
                    "tokens_per_sec": (
                        f"{result.tokens_per_sec:.2f}"
                        if result.tokens_per_sec is not None
                        else ""
                    ),
                    "peak_ram_mb": f"{result.peak_rss_bytes / (1024**2):.1f}",
                    "cpu_percent": f"{result.cpu_percent:.1f}",
                }
            )
            f.flush()

    print(f"\nResults written to {args.output}")


if __name__ == "__main__":
    main()
