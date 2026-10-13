"""Validación de la Fase 1: carga un modelo GGUF con llama-cpp-python y ejecuta un prompt."""

import argparse
import os
import sys

from slm_cpu_serving.metrics import run_inference

DEFAULT_PROMPT = "Explica qué es un modelo de lenguaje pequeño en dos frases."


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ejecuta una inferencia contra un modelo GGUF local."
    )
    parser.add_argument(
        "--model-path",
        default=os.environ.get("MODEL_PATH"),
        help="Ruta a un archivo de modelo GGUF. Por defecto usa la variable de entorno MODEL_PATH.",
    )
    parser.add_argument(
        "--prompt", default=DEFAULT_PROMPT, help="Prompt que se enviará al modelo."
    )
    parser.add_argument(
        "--max-tokens", type=int, default=128, help="Máximo de tokens a generar."
    )
    parser.add_argument(
        "--n-threads", type=int, default=os.cpu_count(), help="Hilos de CPU a usar."
    )
    parser.add_argument("--n-ctx", type=int, default=2048, help="Tamaño de la ventana de contexto.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not args.model_path:
        print(
            "Error: no se indicó la ruta del modelo. Define MODEL_PATH o usa --model-path.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Cargando modelo: {args.model_path}")
    print(f"Prompt: {args.prompt!r}")
    result = run_inference(
        args.model_path,
        args.prompt,
        n_ctx=args.n_ctx,
        n_threads=args.n_threads,
        max_tokens=args.max_tokens,
    )

    print("\n--- Respuesta ---")
    print(result.response)
    print("\n--- Métricas ---")
    print(f"Tiempo de carga:         {result.load_time:.2f}s")
    print(f"Tiempo total:            {result.total_time:.2f}s")
    if result.first_token_latency is not None:
        print(f"Latencia primer token:   {result.first_token_latency:.2f}s")
    if result.tokens:
        print(f"Tokens:                  {result.tokens}")
        print(f"Tokens/s:                {result.tokens_per_sec:.2f}")
    else:
        print("Tokens/s:                no disponible (no se generaron tokens)")
    print(f"Pico de RAM:             {result.peak_rss_bytes / (1024**2):.1f} MB")
    print(
        f"Uso de CPU:              {result.cpu_percent:.1f}% (n_threads={args.n_threads})"
    )


if __name__ == "__main__":
    main()
