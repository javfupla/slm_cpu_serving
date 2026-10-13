"""Challenge: clasifica reseñas con el servidor local en menos de 3 segundos por petición.

Modifica la sección CONFIGURACIÓN (y los parámetros con los que levantas el
servidor) hasta cumplir el objetivo. No cambies las reseñas ni la evaluación.
"""

import argparse
import os
import re
import time
import unicodedata

from openai import OpenAI

# ---------------------------------------------------------------------------
# CONFIGURACIÓN: esto es lo que puedes cambiar
# ---------------------------------------------------------------------------

# Mensaje de sistema con instrucciones para el modelo (o None para no usarlo).
SYSTEM_PROMPT = None

# Prompt que se envía por cada reseña. {review} se sustituye por el texto.
PROMPT_TEMPLATE = "¿Qué opinas de esta reseña?\n\n{review}"

# Máximo de tokens que puede generar el modelo por respuesta.
MAX_TOKENS = 50

# Aleatoriedad de la respuesta (0 = siempre la misma respuesta).
TEMPERATURE = 0

# ---------------------------------------------------------------------------
# A partir de aquí no hace falta tocar nada
# ---------------------------------------------------------------------------

LATENCY_GOAL_S = 3.0
ACCURACY_GOAL = 0.9

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
        description="Challenge: clasifica reseñas con el servidor local en menos de 3 s por petición."
    )
    parser.add_argument(
        "--base-url",
        default=os.environ.get("LLM_BASE_URL", "http://127.0.0.1:8080/v1"),
        help="URL base del servidor compatible con OpenAI.",
    )
    return parser.parse_args()


def extract_label(text: str) -> str | None:
    """Devuelve la primera etiqueta (positiva/negativa/neutral) que aparece en la respuesta."""
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

    # El servidor local no comprueba la API key, pero el SDK de openai exige
    # pasar una, así que usamos un valor cualquiera.
    client = OpenAI(base_url=args.base_url, api_key="dummy")

    print(f"Servidor: {args.base_url}")
    print(f"Clasificando {len(REVIEWS)} reseñas...\n")

    hits = 0
    times = []
    for i, (review, expected) in enumerate(REVIEWS, start=1):
        start = time.perf_counter()
        response = client.chat.completions.create(
            model="local-model",  # el servidor solo tiene un modelo cargado; el nombre no importa
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
            f"[{i:2}] {'OK   ' if hit else 'FALLO'} esperado={expected:<8} "
            f"obtenido={predicted or '?':<8} {elapsed:5.2f}s  {summary!r}"
        )

    accuracy = hits / len(REVIEWS)
    mean_time = sum(times) / len(times)

    print("\n--- Resultado ---")
    print(f"Aciertos:     {hits}/{len(REVIEWS)} ({accuracy:.0%})")
    print(f"Tiempo medio: {mean_time:.2f}s")
    print(f"Tiempo máx.:  {max(times):.2f}s")

    accuracy_ok = accuracy >= ACCURACY_GOAL
    latency_ok = mean_time < LATENCY_GOAL_S
    print(
        f"\nObjetivo: aciertos >= {ACCURACY_GOAL:.0%} {'✅' if accuracy_ok else '❌'}  |  "
        f"tiempo medio < {LATENCY_GOAL_S:.0f}s {'✅' if latency_ok else '❌'}"
    )
    if accuracy_ok and latency_ok:
        print("¡Challenge superado!")


if __name__ == "__main__":
    main()
