# SLM CPU Serving — Repositorio del taller

**Beyond ChatGPT: Real-Time AI Inference on Your Laptop**

En este taller vas a ejecutar un modelo de lenguaje pequeño (SLM, *Small
Language Model*) cuantizado **solo con CPU**, usando
[llama-cpp-python](https://github.com/abetlen/llama-cpp-python). El taller
tiene tres fases:

- **Fase 1:** inferencia local directa desde Python.
- **Fase 2:** servir el modelo como una API compatible con OpenAI.
- **Fase 3:** medir y comparar el rendimiento (benchmarking).

No necesitas GPU, ni API keys, ni servicios de pago.

Las dependencias se gestionan con [uv](https://docs.astral.sh/uv/) mediante
`pyproject.toml` / `uv.lock`. Si no puedes usar Codespaces ni tienes uv, también
puedes instalarlas con `pip` (ver [Alternativa local](#alternativa-local-sin-codespaces)).

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
  01_inferencia_local.py          Fase 1: inferencia local
  02_servidor.md                  Fase 2: guía para levantar el servidor compatible con OpenAI
  02_cliente_api.py               Fase 2: cliente que usa el SDK de openai
  03_benchmark.md                 Fase 3: guía del ejercicio de benchmarking
  03_benchmark.py                 Fase 3: barrido de configuraciones → CSV
```

Si quieres ver cómo funciona la inferencia por dentro, empieza por
[src/slm_cpu_serving/metrics.py](src/slm_cpu_serving/metrics.py).

## Inicio rápido (GitHub Codespaces — recomendado)

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
   uv run python examples/01_inferencia_local.py --model-path models/qwen2.5-1.5b-instruct-q4_k_m.gguf
   ```

   O bien, con el modelo de 3B:

   ```bash
   uv run python examples/01_inferencia_local.py --model-path models/qwen2.5-3b-instruct-q4_k_m.gguf
   ```

   Puedes probar tu propio prompt con `--prompt "..."`. Por defecto el script
   usa todos los núcleos de CPU; para cambiarlo usa `--n-threads N`.

## Alternativa local (sin Codespaces)

Usa esta opción si el Codespace no funciona. Requiere **Python 3.12 o
superior** y **Git**. No hace falta GPU, Docker ni un compilador de C++:
`llama-cpp-python` se instala desde wheels precompilados para CPU.

> **¿Tienes uv instalado?** Basta con `uv sync` y los mismos comandos
> `uv run python ...` que en Codespaces. Los pasos de abajo son para hacerlo
> solo con `pip`.

1. Clona el repositorio:

   ```bash
   git clone https://github.com/leosannlsn/slm_cpu_serving.git
   cd slm_cpu_serving
   ```

2. Crea y activa un entorno virtual e instala el proyecto con sus
   dependencias. La opción `--extra-index-url` apunta a los wheels
   precompilados de `llama-cpp-python`; sin ella, pip intentaría compilar
   llama.cpp desde el código fuente.

   **Windows (PowerShell):**

   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -e . --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu --only-binary llama-cpp-python
   ```

   > Si PowerShell bloquea el script de activación, ejecuta primero
   > `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

   **macOS / Linux:**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e . --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu --only-binary llama-cpp-python
   ```

3. Descarga el modelo. En macOS/Linux usa los mismos comandos del paso 3 de
   Codespaces. En **Windows (PowerShell)** usa `curl.exe`:

   ```powershell
   mkdir models
   curl.exe -L -o models/qwen2.5-1.5b-instruct-q4_k_m.gguf "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf"
   ```

4. Ejecuta el ejemplo (con el entorno virtual activado):

   ```bash
   python examples/01_inferencia_local.py --model-path models/qwen2.5-1.5b-instruct-q4_k_m.gguf
   ```

Cada vez que abras una terminal nueva, recuerda activar el entorno virtual
antes de ejecutar los ejemplos. Con el entorno activado, donde este README o
las guías digan `uv run python`, usa simplemente `python`.

## Fase 1: inferencia local

Ejecuta [examples/01_inferencia_local.py](examples/01_inferencia_local.py)
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

Consulta [examples/02_servidor.md](examples/02_servidor.md) para
levantar un servidor local compatible con OpenAI (`llama_cpp.server`) y luego
ejecuta [examples/02_cliente_api.py](examples/02_cliente_api.py) contra él usando
el SDK de `openai`.

## Fase 3: ejercicio de benchmarking

Consulta [examples/03_benchmark.md](examples/03_benchmark.md) para ejecutar
[examples/03_benchmark.py](examples/03_benchmark.py), que recorre distintas
cantidades de hilos, tamaños de contexto y archivos de modelo, y guarda los
resultados en un CSV para discutirlos en clase.

```bash
uv run python examples/03_benchmark.py --model-path models/qwen2.5-1.5b-instruct-q4_k_m.gguf models/qwen2.5-3b-instruct-q4_k_m.gguf --n-threads 1 2 --n-ctx 512 2048 --max-tokens 64 --output benchmark_results.csv
```

El reto: obtener tus propios números, compararlos y explicar las diferencias.
Las preguntas para la discusión están en
[examples/03_benchmark.md](examples/03_benchmark.md).
