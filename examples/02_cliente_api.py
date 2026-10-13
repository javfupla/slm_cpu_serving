"""Validación de la Fase 2: conversa con un llama_cpp.server local usando el SDK de OpenAI."""

import argparse
import os
import time

from openai import OpenAI

DEFAULT_PROMPT = "Explica qué es un modelo de lenguaje pequeño en dos frases."


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Envía una petición de chat completion a un servidor local compatible con OpenAI."
    )
    parser.add_argument(
        "--base-url",
        default=os.environ.get("LLM_BASE_URL", "http://127.0.0.1:8080/v1"),
        help="URL base del servidor compatible con OpenAI.",
    )
    parser.add_argument(
        "--prompt", default=DEFAULT_PROMPT, help="Prompt que se enviará al modelo."
    )
    parser.add_argument(
        "--max-tokens", type=int, default=128, help="Máximo de tokens a generar."
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # El servidor local no comprueba la API key, pero el SDK de openai exige
    # pasar una, así que usamos un valor cualquiera.
    client = OpenAI(base_url=args.base_url, api_key="dummy")

    print(f"Servidor: {args.base_url}")
    print(f"Prompt:   {args.prompt!r}")

    start = time.perf_counter()
    response = client.chat.completions.create(
        model="local-model",  # el servidor solo tiene un modelo cargado; el nombre no importa
        messages=[{"role": "user", "content": args.prompt}],
        max_tokens=args.max_tokens,
    )
    elapsed = time.perf_counter() - start

    content = response.choices[0].message.content
    usage = response.usage

    print("\n--- Respuesta ---")
    print(content)
    print("\n--- Métricas ---")
    print(f"Tiempo total: {elapsed:.2f}s")
    if usage and usage.completion_tokens:
        print(f"Tokens:       {usage.completion_tokens}")
        print(f"Tokens/s:     {usage.completion_tokens / elapsed:.2f}")


if __name__ == "__main__":
    main()
