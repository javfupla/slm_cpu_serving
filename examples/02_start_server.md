# Fase 2: levantar un servidor compatible con OpenAI

`llama-cpp-python` incluye un servidor propio (`llama_cpp.server`) que expone
una API HTTP compatible con OpenAI sobre el mismo modelo GGUF que usamos en
[01_local_inference.py](01_local_inference.py).

¿Por qué importa esto? Muchas aplicaciones y librerías ya saben "hablar" con la
API de OpenAI. Si nuestro servidor local imita esa API, podemos cambiar un
servicio en la nube por un modelo propio cambiando solo la URL.

## Iniciar el servidor

```bash
uv run python -m llama_cpp.server --model models/qwen2.5-1.5b-instruct-q4_k_m.gguf --n_ctx 2048 --n_threads 2 --port 8080
```

Deja esto corriendo en su propia terminal. En Codespaces, VS Code reenviará
automáticamente el puerto 8080: abre la pestaña **Ports** para confirmar que
aparece y deja su visibilidad en **Private** (valor por defecto), a menos que
quieras compartirlo.

## Verificar que está funcionando

```bash
curl http://127.0.0.1:8080/v1/models
```

Debería devolver una lista JSON con el modelo cargado.

## Ejecutar el cliente

Con el servidor todavía corriendo, en una segunda terminal:

```bash
uv run python examples/03_api_client.py
```

Este script usa el SDK de `openai` apuntando a `http://127.0.0.1:8080/v1` para
enviar una petición de *chat completion*: es decir, le manda un mensaje al
modelo y recibe su respuesta, como cuando escribes en ChatGPT. La diferencia es
que aquí el "ChatGPT" es el modelo que corre en tu propia máquina. El código es
el mismo que usarías con la API real de OpenAI; solo cambian la URL del
servidor y el modelo al que se le pide la respuesta.
