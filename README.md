# SLM CPU Serving — Repositorio del taller

**Beyond ChatGPT: Real-Time AI Inference on Your Laptop**

En este taller vas a ejecutar un modelo de lenguaje pequeño (SLM, *Small
Language Model*) cuantizado **solo con CPU**, usando
[llama-cpp-python](https://github.com/abetlen/llama-cpp-python). El taller
tiene cuatro fases:

- **Fase 1:** inferencia local directa desde Python.
- **Fase 2:** servir el modelo como una API compatible con OpenAI.
- **Fase 3:** medir y comparar el rendimiento (benchmarking).
- **Fase 4:** challenge: construir un clasificador rápido y preciso.

No necesitas GPU, ni API keys, ni servicios de pago.

Las dependencias se gestionan con [uv](https://docs.astral.sh/uv/) mediante
`pyproject.toml` / `uv.lock`. Si no puedes usar Codespaces o algún servicio
externo falla, consulta [fallback.md](fallback.md).

## Conceptos clave

Un resumen rápido de los términos que usaremos (la presentación del taller
los explica en detalle):

| Concepto | Qué significa |
|----------|---------------|
| **Inferencia** | Usar un modelo ya entrenado para generar una respuesta. Los pesos no cambian: solo se pasa la entrada por la red para obtener la salida. |
| **Modelo** | Archivo con los pesos de la red neuronal ya entrenada. En este taller usamos Qwen2.5-Instruct en formato **GGUF**, el formato de archivo de llama.cpp para modelos cuantizados (los `.gguf` de la carpeta `models/`). |
| **Motor de inferencia (llama.cpp)** | Programa que carga el modelo y hace los cálculos para generar texto. Usamos [llama.cpp](https://github.com/ggml-org/llama.cpp), optimizado para CPU, a través de `llama-cpp-python`, que nos permite usarlo desde Python. |
| **SLM** | Modelo de lenguaje "pequeño" (aquí, 1.5B y 3B parámetros) que cabe en la RAM de una laptop. |
| **Cuantización** | Guardar los pesos con menos bits (p. ej. 4 bits en lugar de 16) para reducir memoria y acelerar la CPU, a cambio de algo de precisión. `Q4_K_M` es un formato de ~4 bits. |
| **Token y tokenizador** | El modelo no lee texto, sino *tokens*: fragmentos de texto (aprox. una sílaba o palabra corta) representados como números. El **tokenizador** convierte el texto en tokens y viceversa; cada modelo trae el suyo. El mismo texto puede dar distinta cantidad de tokens según el idioma. |
| **Latencia del primer token** | Tiempo desde que envías el prompt hasta que aparece el primer token. Es lo que el usuario percibe como "tiempo de reacción". |
| **Throughput (tokens/s)** | Velocidad de generación una vez que el modelo empezó a responder. |
| **Ventana de contexto (`n_ctx`)** | Cantidad máxima de tokens (prompt + respuesta) que el modelo puede "recordar" a la vez. |
| **Hilos (`n_threads`)** | Número de hilos de CPU que usa llama.cpp para el cálculo. |

## Estructura del repositorio

```text
.devcontainer/devcontainer.json   Configuración de Codespaces
pyproject.toml / uv.lock          Dependencias del proyecto
src/slm_cpu_serving/
  metrics.py                      Carga el modelo, ejecuta el prompt y mide tiempos/RAM/CPU
examples/
  01_local_inference.py           Fase 1: inferencia local
  02_start_server.md              Fase 2: guía para levantar el servidor compatible con OpenAI
  03_api_client.py                Fase 2: cliente que usa el SDK de openai
  04_benchmark.py                 Fase 3: barrido de configuraciones → CSV
  05_benchmark.md                 Fase 3: guía del ejercicio de benchmarking
  06_challenge.md                 Fase 4: guía del challenge
  07_challenge.py                 Fase 4: clasificador de reseñas que debes optimizar
```

Si quieres ver cómo funciona la inferencia por dentro, empieza por
[src/slm_cpu_serving/metrics.py](src/slm_cpu_serving/metrics.py).

## Quick start (GitHub Codespaces — recomendado)

1. En GitHub, haz clic en **Code → Codespaces → Create codespace on main**.
2. Espera a que se construya el contenedor. El `postCreateCommand` ejecuta
   `uv sync` automáticamente y crea `.venv` con todas las dependencias.
3. Descarga un modelo cuantizado (solo una vez, ~1 GB):

   ```bash
   mkdir -p models
   curl -L -o models/qwen2.5-1.5b-instruct-q4_k_m.gguf "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf"
   ```

   Opcionalmente, descarga el modelo preferido (más grande) (solo una vez, ~2 GB):

   ```bash
   mkdir -p models
   curl -L -o models/qwen2.5-3b-instruct-q4_k_m.gguf "https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct-q4_k_m.gguf"
   ```

4. Ejecuta el ejemplo:

   ```bash
   uv run python examples/01_local_inference.py --model-path models/qwen2.5-1.5b-instruct-q4_k_m.gguf
   ```

   O bien, con el modelo de 3B:

   ```bash
   uv run python examples/01_local_inference.py --model-path models/qwen2.5-3b-instruct-q4_k_m.gguf
   ```

   Puedes probar tu propio prompt con `--prompt "..."`. Por defecto el script
   usa todos los núcleos de CPU; para cambiarlo usa `--n-threads N`.

## Alternativa si algo falla (contingencias)

Si Codespaces, GitHub, PyPI o Hugging Face no están disponibles, o la conexión
es inestable, consulta [fallback.md](fallback.md): recoge todas las situaciones
posibles, con la instalación local, el wheelhouse offline y el modelo
descargado previamente.

## Fase 1: inferencia local

Ejecuta [examples/01_local_inference.py](examples/01_local_inference.py)
(ver el inicio rápido). Al terminar, el script muestra la respuesta del modelo
y estas métricas:

- Tiempo de carga del modelo
- Latencia del primer token
- Tiempo total y tokens/s
- RAM pico y uso de CPU

> **Nota:** un uso de CPU mayor a 100% significa que el proceso está usando
> más de un núcleo (100% = un núcleo completo).

Prueba con los dos modelos (1.5B y 3B) y anota las diferencias: las usaremos en
la Fase 3.

## Fase 2: servir el modelo con una API compatible con OpenAI

Consulta [examples/02_start_server.md](examples/02_start_server.md) para
levantar un servidor local compatible con OpenAI (`llama_cpp.server`) y luego
ejecuta [examples/03_api_client.py](examples/03_api_client.py) contra él usando
el SDK de `openai`.

## Fase 3: ejercicio de benchmarking

Consulta [examples/05_benchmark.md](examples/05_benchmark.md) para ejecutar
[examples/04_benchmark.py](examples/04_benchmark.py), que recorre distintas
cantidades de hilos, máximos de tokens de salida y archivos de modelo, y guarda
los resultados en un CSV para discutirlos en clase.

```bash
uv run python examples/04_benchmark.py --model-path models/qwen2.5-1.5b-instruct-q4_k_m.gguf models/qwen2.5-3b-instruct-q4_k_m.gguf --n-threads 1 2 --max-tokens 16 64 --output benchmark_results.csv
```

El objetivo: obtener tus propios números, compararlos y explicar las
diferencias. Las preguntas para la discusión están en
[examples/05_benchmark.md](examples/05_benchmark.md).

## Fase 4: challenge

Usa todo lo anterior para construir un clasificador de reseñas (positiva /
negativa / neutral) que acierte al menos 18 de 20 y responda en menos de 3
segundos por reseña. Las reglas y las pistas están en
[examples/06_challenge.md](examples/06_challenge.md); el script a optimizar es
[examples/07_challenge.py](examples/07_challenge.py).
