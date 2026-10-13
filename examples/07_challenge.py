"""Challenge: classify reviews with the local server in under 3 seconds per request.

Edit the CONFIGURATION section (and the parameters you start the server with)
until you reach the goal. Do not change the reviews or the evaluation.
"""

import argparse
import os
import re
import time
import unicodedata

from openai import OpenAI

# ---------------------------------------------------------------------------
# CONFIGURATION: this is what you can change
# ---------------------------------------------------------------------------

# System message with instructions for the model (or None to skip it).
SYSTEM_PROMPT = None

# Prompt sent for each review. {review} is replaced with the review text.
PROMPT_TEMPLATE = "¿Qué opinas de esta reseña?\n\n{review}"

# Maximum number of tokens the model may generate per response.
MAX_TOKENS = 50

# Randomness of the response (0 = always the same response).
TEMPERATURE = 0

# ---------------------------------------------------------------------------
# Nothing below this line needs to be changed
# ---------------------------------------------------------------------------

LATENCY_GOAL_S = 3.0
ACCURACY_GOAL = 0.9

# Reviews are in Spanish, with their expected labels (positiva/negativa/neutral).
REVIEWS = [
    ("El envío llegó en dos días y el producto funciona perfecto. Lo recomiendo.", "positiva"),
    ("La batería no dura ni medio día. Una decepción total, no lo volvería a comprar.", "negativa"),
    ("Cumple su función. Ni bueno ni malo, lo normal para su precio.", "neutral"),
    ("Increíble calidad de sonido, superó todas mis expectativas.", "positiva"),
    ("Llegó roto y el servicio de atención al cliente nunca respondió.", "negativa"),
    ("El color es algo distinto al de las fotos, pero por lo demás es lo que esperaba.", "neutral"),
    ("Muy cómodo y fácil de usar. Mi familia también está encantada.", "positiva"),
    ("Se calienta muchísimo y a la semana dejó de encender.", "negativa"),
    ("Lo uso de vez en cuando; hace lo que dice la descripción, sin más.", "neutral"),
    ("Pésima compra: las instrucciones no sirven y faltaban piezas.", "negativa"),
    ("Lo compré para regalar y fue un acierto, la calidad es excelente.", "positiva"),
    ("Es correcto. Hay opciones mejores, pero también peores.", "neutral"),
    ("Pedí talla M y me llegó una S; la devolución fue un infierno.", "negativa"),
    ("La pantalla se ve genial y la batería dura todo el día.", "positiva"),
    ("Llegó a tiempo y bien embalado; todavía no lo he usado mucho.", "neutral"),
    ("Hace un ruido insoportable y huele a plástico quemado.", "negativa"),
    ("Atención al cliente de diez: me resolvieron el problema en minutos.", "positiva"),
    ("El tamaño es el indicado y hace su trabajo, nada especial.", "neutral"),
    ("Tras un mes de uso la tela ya está rota. No lo recomiendo.", "negativa"),
    ("Ligero, bonito y muy rápido. Estoy encantado con la compra.", "positiva"),
]

LABEL_PATTERN = re.compile(r"\b(positiv|negativ|neutr)\w*")
LABELS = {"positiv": "positiva", "negativ": "negativa", "neutr": "neutral"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Challenge: classify reviews with the local server in under 3 s per request."
    )
    parser.add_argument(
        "--base-url",
        default=os.environ.get("LLM_BASE_URL", "http://127.0.0.1:8080/v1"),
        help="Base URL of the OpenAI-compatible server.",
    )
    return parser.parse_args()


def extract_label(text: str) -> str | None:
    """Return the first label (positiva/negativa/neutral) found in the response."""
    normalized = unicodedata.normalize("NFKD", text.lower())
    normalized = "".join(c for c in normalized if not unicodedata.combining(c))
    match = LABEL_PATTERN.search(normalized)
    return LABELS[match.group(1)] if match else None


def build_messages(review: str) -> list[dict[str, str]]:
    messages = []
    if SYSTEM_PROMPT:
        messages.append({"role": "system", "content": SYSTEM_PROMPT})
    messages.append({"role": "user", "content": PROMPT_TEMPLATE.format(review=review)})
    return messages


def main() -> None:
    args = parse_args()

    # The local server does not check the API key, but the openai SDK requires
    # one, so any value will do.
    client = OpenAI(base_url=args.base_url, api_key="dummy")

    print(f"Server: {args.base_url}")
    print(f"Classifying {len(REVIEWS)} reviews...\n")

    hits = 0
    times = []
    for i, (review, expected) in enumerate(REVIEWS, start=1):
        start = time.perf_counter()
        response = client.chat.completions.create(
            model="local-model",  # the server only has one model loaded; the name does not matter
            messages=build_messages(review),
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
        )
        elapsed = time.perf_counter() - start
        times.append(elapsed)

        answer = response.choices[0].message.content or ""
        predicted = extract_label(answer)
        hit = predicted == expected
        hits += hit

        summary = " ".join(answer.split())
        if len(summary) > 60:
            summary = summary[:57] + "..."
        print(
            f"[{i:2}] {'OK  ' if hit else 'FAIL'} expected={expected:<8} "
            f"got={predicted or '?':<8} {elapsed:5.2f}s  {summary!r}"
        )

    accuracy = hits / len(REVIEWS)
    mean_time = sum(times) / len(times)

    print("\n--- Result ---")
    print(f"Correct:   {hits}/{len(REVIEWS)} ({accuracy:.0%})")
    print(f"Mean time: {mean_time:.2f}s")
    print(f"Max time:  {max(times):.2f}s")

    accuracy_ok = accuracy >= ACCURACY_GOAL
    latency_ok = mean_time < LATENCY_GOAL_S
    print(
        f"\nGoal: accuracy >= {ACCURACY_GOAL:.0%} {'✅' if accuracy_ok else '❌'}  |  "
        f"mean time < {LATENCY_GOAL_S:.0f}s {'✅' if latency_ok else '❌'}"
    )
    if accuracy_ok and latency_ok:
        print("Challenge completed!")


if __name__ == "__main__":
    main()
