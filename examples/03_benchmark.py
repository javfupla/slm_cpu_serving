"""Benchmarking de la Fase 3: recorre cantidades de hilos, tamaños de contexto y modelos.

Escribe una fila de CSV por cada combinación (model, n_threads, n_ctx) para que
los resultados sean fáciles de llevar a una hoja de cálculo o discutir en clase.
"""

import argparse
import csv
import os
import sys
from pathlib import Path

from slm_cpu_serving.metrics import run_inference

DEFAULT_PROMPT = "Explica qué es un modelo de lenguaje pequeño en dos oraciones."

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
        description="Mide la inferencia variando cantidad de hilos, tamaños de contexto y modelos."
    )
    parser.add_argument(
        "--model-path",
        nargs="+",
        required=True,
        help="Uno o más archivos GGUF a medir (p. ej. distintos tamaños/niveles de cuantización).",
    )
    parser.add_argument(
        "--n-threads",
        type=int,
        nargs="+",
        default=[os.cpu_count()],
        help="Cantidades de hilos a probar.",
    )
    parser.add_argument(
        "--n-ctx",
        type=int,
        nargs="+",
        default=[2048],
        help="Tamaños de ventana de contexto a probar.",
    )
    parser.add_argument(
        "--prompt", default=DEFAULT_PROMPT, help="Prompt que se enviará al modelo."
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=128,
        help="Máximo de tokens a generar por ejecución.",
    )
    parser.add_argument(
        "--repeats", type=int, default=1, help="Número de repeticiones por combinación."
    )
    parser.add_argument(
        "--output",
        default="benchmark_results.csv",
        help="Ruta donde escribir el CSV de resultados.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    for model_path in args.model_path:
        if not Path(model_path).is_file():
            print(f"Error: no se encontró el archivo del modelo: {model_path}", file=sys.stderr)
            sys.exit(1)

    combinations = [
        (model_path, n_threads, n_ctx)
        for model_path in args.model_path
        for n_threads in args.n_threads
        for n_ctx in args.n_ctx
        for _ in range(args.repeats)
    ]

    print(f"Ejecutando {len(combinations)} combinación(es) de benchmark...")

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

    print(f"\nResultados guardados en {args.output}")


if __name__ == "__main__":
    main()
