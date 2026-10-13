#!/usr/bin/env python3

import os
import sys
import platform
import importlib
from pathlib import Path

REQUIRED_PYTHON = (3, 12)

REQUIRED_PACKAGES = [
    "openai",
    "psutil",
    "llama_cpp",
]

MODEL_ENV_VAR = "MODEL_PATH"


def ok(msg):
    print(f"✅ {msg}")


def fail(msg):
    print(f"❌ {msg}")


def warn(msg):
    print(f"⚠️  {msg}")


errors = 0

print("\n=== SLM Workshop Environment Check ===\n")

#
# Python version
#
print("Python")

if sys.version_info >= REQUIRED_PYTHON:
    ok(f"Python {platform.python_version()}")
else:
    fail(
        f"Python {platform.python_version()} detected "
        f"(requires {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]}+)"
    )
    errors += 1

#
# Platform
#
print("\nPlatform")

ok(
    f"{platform.system()} "
    f"{platform.release()} "
    f"({platform.machine()})"
)

#
# Dependencies
#
print("\nDependencies")

for package in REQUIRED_PACKAGES:
    try:
        importlib.import_module(package)
        ok(package)
    except Exception as ex:
        fail(f"{package}: {ex}")
        errors += 1

#
# Model
#
print("\nModel")

model_path = os.environ.get(MODEL_ENV_VAR)

if model_path:
    model_file = Path(model_path)

    if model_file.exists():
        size_gb = model_file.stat().st_size / (1024**3)
        ok(f"Model found: {model_file.name}")
        ok(f"Model size: {size_gb:.2f} GB")
    else:
        fail(f"MODEL_PATH points to missing file: {model_path}")
        errors += 1
else:
    warn(
        "MODEL_PATH environment variable not set "
        "(inference test skipped)"
    )

#
# Memory
#
print("\nMemory")

try:
    import psutil

    total_gb = psutil.virtual_memory().total / (1024**3)

    if total_gb >= 16:
        ok(f"{total_gb:.1f} GB RAM (recommended)")
    elif total_gb >= 8:
        warn(f"{total_gb:.1f} GB RAM (minimum)")
    else:
        fail(f"{total_gb:.1f} GB RAM (<8 GB)")
        errors += 1

except Exception as ex:
    warn(f"Unable to determine RAM: {ex}")

#
# Optional inference test
#
print("\nInference")

if model_path and Path(model_path).exists():
    try:
        from llama_cpp import Llama

        llm = Llama(
            model_path=model_path,
            n_ctx=512,
            verbose=False,
        )

        result = llm(
            "Say hello in fewer than five words.",
            max_tokens=10,
        )

        text = (
            result["choices"][0]["text"]
            .strip()
            .replace("\n", " ")
        )

        ok("Inference test passed")
        print(f"    Response: {text}")

    except Exception as ex:
        fail(f"Inference test failed: {ex}")
        errors += 1
else:
    warn("Inference test skipped")

#
# Summary
#
print("\n=== Summary ===")

if errors == 0:
    ok("Environment is workshop-ready")
else:
    fail(f"{errors} issue(s) detected")

sys.exit(1 if errors else 0)