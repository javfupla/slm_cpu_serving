# Fase 3: ejercicio de benchmarking

[examples/04_benchmark.py](04_benchmark.py) recorre combinaciones de cantidad
de hilos, tamaños de contexto y archivos de modelo, y escribe una fila de CSV
por cada combinación. Los estudiantes pueden analizar los compromisos
(*trade-offs*) variando:

- **Cantidad de hilos** — `--n-threads`
- **Tamaños de contexto** — `--n-ctx`
- **Niveles de cuantización / tamaños de modelo** — pasa varios valores en
  `--model-path` (p. ej. un GGUF Q4_K_M y uno Q5_K_M/Q8_0, o los modelos de
  1.5B y 3B)

## Ejecutar un barrido

```bash
uv run python examples/04_benchmark.py --model-path models/qwen2.5-1.5b-instruct-q4_k_m.gguf models/qwen2.5-3b-instruct-q4_k_m.gguf --n-threads 1 2 4 --n-ctx 512 2048 --max-tokens 64 --output benchmark_results.csv
```

Cada combinación se ejecuta una vez por defecto; usa `--repeats 3` para
promediar el ruido antes de discutir los resultados en clase.

## Salida

Un CSV con las columnas: `model, n_threads, n_ctx, load_time_s,
first_token_latency_s, total_time_s, tokens, tokens_per_sec, peak_ram_mb,
cpu_percent`, fácil de abrir en una hoja de cálculo o graficar durante el
taller.

| Columna | Significado |
|---------|-------------|
| `model` | Archivo GGUF usado |
| `n_threads` | Hilos de CPU |
| `n_ctx` | Tamaño de la ventana de contexto |
| `load_time_s` | Tiempo de carga del modelo (s) |
| `first_token_latency_s` | Latencia hasta el primer token (s) |
| `total_time_s` | Tiempo total de generación (s) |
| `tokens` | Tokens generados |
| `tokens_per_sec` | Throughput (tokens/s) |
| `peak_ram_mb` | Pico de memoria RAM (MB) |
| `cpu_percent` | Uso de CPU (100% = un núcleo) |

## Preguntas para discutir

- ¿Duplicar los hilos duplica los tokens/s? ¿Por qué sí o por qué no?
- ¿Qué cambia más con el tamaño del modelo: la latencia o la RAM?
- ¿Cambia algo usar un contexto de 512 o de 2048 tokens? ¿En qué situaciones
  esperarías que sí importara?
- ¿Por qué la primera ejecución puede tardar más en cargar el modelo que las
  siguientes? ¿Qué implica eso al medir rendimiento?
- Si tuvieras que responder en menos de 3 segundos, ¿qué configuración
  elegirías?
