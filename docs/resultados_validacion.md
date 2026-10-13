# Resultados de validación (referencia para quien imparte el taller)

> Este documento **no es material para los alumnos**: contiene los números y
> las conclusiones que ellos deberían obtener en los ejercicios. Se guarda como
> referencia de que el entorno funciona (Codespaces y Windows local) y como
> "solucionario" de la discusión. Puede moverse fuera del repo o borrarse antes
> del taller.

## Fase 1: inferencia local

Modelo de respaldo (Qwen2.5-1.5B-Instruct Q4_K_M, ~1 GB), validado en Codespaces:

| Métrica                     | Valor |
|-----------------------------|-------|
| Tamaño del modelo           | ~1 GB (Q4_K_M) |
| Uso de RAM                  | 1834.3 MB (pico) |
| Uso de CPU                  | 165.0% (n_threads=2) |
| Tiempo de carga             | 1.24s |
| Latencia del primer token   | 1.93s |
| Latencia total              | 6.39s |
| Tokens/s                    | 7.36  |

Modelo preferido (Qwen2.5-3B-Instruct Q4_K_M, ~2 GB), validado localmente
(Windows, 2 hilos):

| Métrica                     | Valor |
|-----------------------------|-------|
| Tamaño del modelo           | ~2 GB (Q4_K_M) |
| Uso de RAM                  | 3292.2 MB (pico) |
| Uso de CPU                  | 245.1% (n_threads=2) |
| Tiempo de carga             | 1.83s |
| Latencia del primer token   | 0.68s |
| Latencia total              | 5.78s |
| Tokens/s                    | 7.96  |

Modelo preferido (Qwen2.5-3B-Instruct Q4_K_M, ~2 GB), validado en Codespaces
(2 hilos):

| Métrica                     | Valor |
|-----------------------------|-------|
| Tamaño del modelo           | ~2 GB (Q4_K_M) |
| Uso de RAM                  | 3464.2 MB (pico) |
| Uso de CPU                  | 99.1% (n_threads=2) |
| Latencia del primer token   | 2.90s |
| Latencia total              | 13.71s |
| Tokens/s                    | 4.16  |

> **Nota:** un uso de CPU mayor a 100% significa que el proceso está usando
> más de un núcleo (100% = un núcleo completo).

El modelo de 3B aproximadamente duplica el uso de RAM (~1.8 GB → ~3.3 GB pico),
pero cabe sin problemas en la máquina por defecto de Codespaces (2 núcleos /
8 GB), con margen de sobra para usarlo en clase.

## Fase 2: servir el modelo con una API compatible con OpenAI

Validado localmente (Windows, 2 hilos, mismo modelo 1.5B Q4_K_M):

| Métrica      | Valor |
|--------------|-------|
| Tiempo total | 2.78s |
| Tokens       | 30    |
| Tokens/s     | 10.80 |

Validado en Codespaces (mismo modelo 1.5B Q4_K_M):

| Métrica      | Valor |
|--------------|-------|
| Tiempo total | 7.21s |
| Tokens       | 48    |
| Tokens/s     | 6.65  |

## Fase 3: ejercicio de benchmarking

Comando usado:

```bash
python examples/03_benchmark.py --model-path models/qwen2.5-1.5b-instruct-q4_k_m.gguf models/qwen2.5-3b-instruct-q4_k_m.gguf --n-threads 1 2 --n-ctx 512 2048 --max-tokens 64 --output benchmark_results.csv
```

Validado en Codespaces:

| Modelo | Hilos | Contexto | Tiempo total | Tokens/s | RAM pico  | Uso de CPU |
|--------|-------|----------|--------------|----------|-----------|------------|
| 1.5B   | 1     | 512      | 8.01s        | 5.87     | 1790.7 MB | 109.5%     |
| 1.5B   | 1     | 2048     | 7.86s        | 5.98     | 1835.9 MB | 109.2%     |
| 1.5B   | 2     | 512      | 6.12s        | 7.69     | 1797.3 MB | 171.2%     |
| 1.5B   | 2     | 2048     | 6.32s        | 7.43     | 1853.6 MB | 169.2%     |
| 3B     | 1     | 512      | 17.28s       | 3.30     | 3427.5 MB | 76.3%      |
| 3B     | 1     | 2048     | 17.43s       | 3.27     | 3481.9 MB | 112.0%     |
| 3B     | 2     | 512      | 13.98s       | 4.08     | 3417.1 MB | 174.1%     |
| 3B     | 2     | 2048     | 17.45s       | 3.27     | 3489.2 MB | 154.1%     |

Observaciones para la discusión en clase:

- **La cantidad de hilos** es lo que más impacta: pasar de 1 → 2 hilos mejora
  los tokens/s en ~25-30% en ambos modelos.
- **El tamaño de contexto** (512 vs 2048) casi no cambia los tokens/s ni la RAM
  para respuestas cortas. Un contexto más grande importa sobre todo cuando el
  prompt o el historial crecen, no para la velocidad de generación en sí.
- **El tamaño del modelo** reduce el throughput aproximadamente a la mitad y
  casi duplica la RAM pico al pasar de 1.5B → 3B: un ejemplo claro del
  equilibrio entre calidad, latencia y recursos.
- El tiempo de carga de 12s en la fila 3B / 1 hilo / contexto 512 (ver el CSV
  completo) se debió a que el archivo de 2 GB no estaba aún en la caché del
  sistema de archivos (*cold cache*) en la primera lectura. Es un buen momento
  para explicar por qué los benchmarks deberían descartar la primera ejecución
  o "calentar" la caché.

> **Nota:** los prompts por defecto de los scripts están en español; los números
> de estas tablas se midieron con el prompt original en inglés, así que tus
> resultados pueden variar ligeramente.

## Fase 4: challenge (soluciones de referencia)

Medido en local (Windows, CPU de escritorio) con el servidor a `--n_threads 2`.
Esta CPU es mucho más rápida que un Codespace, así que **los tiempos absolutos
no son representativos**: hay que validar en Codespaces que el objetivo de 3 s
se puede cumplir con el modelo de 1.5B y ver dónde queda el de 3B.

| Configuración | Modelo | Aciertos | Tiempo medio |
|---------------|--------|----------|--------------|
20 reseñas (7 positivas, 7 negativas, 6 neutrales); objetivo: **≥ 90 %
(18/20)** y tiempo medio < 3 s.

| Configuración | Modelo | Aciertos | Tiempo medio |
|---------------|--------|----------|--------------|
| Inicial (prompt abierto, `MAX_TOKENS = 50`, `TEMPERATURE = 0`) | 1.5B | 14/20 | 2.02s |
| Inicial | 3B | 10/20 | 3.76s |
| Inicial con `MAX_TOKENS = 100` (dos ejecuciones) | 1.5B | 15/20 y 16/20 | ~3.2s |
| "Responde solo con una palabra", `MAX_TOKENS = 3`, `TEMPERATURE = 0` | 1.5B | 15/20 | 0.20s |
| Igual + definición de cada categoría en el `SYSTEM_PROMPT` | 1.5B | 18/20 | 0.20s |
| "Responde solo con una palabra", `MAX_TOKENS = 3`, `TEMPERATURE = 0` | 3B | 20/20 | 0.33s |
| Igual + definición de cada categoría en el `SYSTEM_PROMPT` | 3B | 20/20 | 0.36s |

El script busca la primera etiqueta que aparece en la respuesta, así que con la
configuración inicial (respuestas largas) el modelo ya acierta bastantes, pero
se queda lejos del 90 %. Con un objetivo del 80 % la inicial llegaba a veces
por sí sola (16/20 con `MAX_TOKENS = 100`); por eso el objetivo es del 90 %.

Cambiar al modelo de 3B sin tocar nada más **no basta**: con respuestas largas
acierta incluso menos (el texto se corta antes de dar la etiqueta) y es lento.

El reto extra con el 1.5B queda **justo** (18/20): cualquier fallo de más lo
deja fuera. Conviene comprobarlo en Codespaces; si no se alcanza, se puede
bajar el objetivo del reto extra o mejorar la definición de "neutral".

La solución esperada del challenge es el 3B con respuestas de una palabra; el
**reto extra** (hacerlo con el 1.5B) obliga a definir las categorías en el
`SYSTEM_PROMPT`.

Lecciones que deberían salir:

- **El tiempo lo dominan los tokens generados**: pedir una sola palabra y
  limitar `MAX_TOKENS` baja el tiempo de ~2–4 s a menos de 0.5 s sin cambiar de
  modelo.
- **La velocidad no arregla la calidad**: con respuestas cortas, el 1.5B
  clasifica todas las reseñas neutrales como positivas. Hace falta mejorar el
  prompt (definir "neutral") o usar un modelo más grande.
- **Calidad vs. latencia**: el 3B acierta todo incluso con un prompt simple,
  pero es ~1.6× más lento; en Codespaces eso puede acercarlo o pasarlo del
  límite de 3 s.

`SYSTEM_PROMPT` usado en las filas "con definición":

```text
Clasifica el sentimiento de reseñas de productos. Responde solo con una palabra:
- positiva: el cliente está contento y lo recomienda.
- negativa: el cliente está descontento o el producto falla.
- neutral: la opinión es tibia o mixta; el producto cumple, sin entusiasmo ni quejas graves.
```

con `PROMPT_TEMPLATE = "Reseña: {review}"`.

Me falta probar en el codespace para ver si es asequible sacar
