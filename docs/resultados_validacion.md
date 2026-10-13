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
