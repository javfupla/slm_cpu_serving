# Fase 4: challenge — un clasificador en menos de 3 segundos

Una tienda online quiere clasificar automáticamente las reseñas de sus clientes
como **positiva**, **negativa** o **neutral**, usando solo CPU y sin pagar por
una API externa. Tu misión: conseguirlo con el modelo local.

[04_challenge.py](04_challenge.py) envía 20 reseñas al servidor de la Fase 2,
compara cada respuesta con la etiqueta correcta y mide cuánto tarda.

## Objetivo

- **Aciertos ≥ 90 %** (al menos 18 de 20 reseñas bien clasificadas)
- **Tiempo medio < 3 s** por reseña

Los objetivos están pensados para un Codespace (2 núcleos). En una laptop
potente será más fácil: prueba a levantar el servidor con `--n_threads 2` o
`--n_threads 1` para ponerte en las mismas condiciones.

## Cómo empezar

1. Levanta el servidor como en [02_servidor.md](02_servidor.md) y déjalo
   corriendo en su terminal.
2. En otra terminal, ejecuta el challenge con la configuración inicial:

   ```bash
   uv run python examples/04_challenge.py
   ```

   La configuración inicial **no cumple el objetivo** (y puede tardar un par
   de minutos): ese es tu punto de partida.

3. Modifica y vuelve a ejecutar hasta superar el challenge.

## Qué puedes cambiar

- En [04_challenge.py](04_challenge.py), la sección **CONFIGURACIÓN**:
  - `SYSTEM_PROMPT`: instrucciones generales para el modelo.
  - `PROMPT_TEMPLATE`: cómo se le presenta cada reseña.
  - `MAX_TOKENS`: cuántos tokens puede generar como máximo.
  - `TEMPERATURE`: cuánta aleatoriedad tiene la respuesta. Empieza en 0 para
    que, al repetir una ejecución, los resultados sean (casi) iguales y puedas
    comparar tus cambios.
- Al levantar el servidor: el modelo (`--model`, 1.5B o 3B), `--n_threads` y
  `--n_ctx`.

No cambies las reseñas ni la forma de evaluar.

<details>
<summary>Pistas (ábrelas solo si te atascas)</summary>

- Mira las respuestas en la salida: ¿cuántas palabras escribe el modelo para
  dar una etiqueta? Recuerda que cada token generado cuesta tiempo.
- Puedes pedirle al modelo que responda con una sola palabra… y limitar
  `MAX_TOKENS` para asegurarte.
- ¿El modelo más grande acierta más? ¿Cuánto más tarda?

</details>

## Reto extra: hazlo con el modelo pequeño

¿Lo conseguiste con el modelo de 3B? Ahora intenta superar el challenge con el
de **1.5B**: es más rápido y usa la mitad de RAM, pero se equivoca más. Tendrás
que compensarlo con un mejor prompt.

<details>
<summary>Pista</summary>

- Mira qué categoría confunde el modelo pequeño y explícale qué significa cada
  una en el `SYSTEM_PROMPT`.

</details>

## Para discutir

- ¿Qué cambio redujo más el tiempo? ¿Por qué?
- ¿Qué categoría le costó más al modelo? ¿Cómo lo resolviste?
- ¿Conseguiste el reto extra? ¿Qué te dio más resultado: un modelo más grande
  o un prompt mejor?
- Si esto fuera un servicio real con miles de reseñas por hora, ¿qué más
  tendrías que medir?
