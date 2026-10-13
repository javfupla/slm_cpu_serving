"""Shared inference + resource-measurement helpers for the example scripts."""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass

import psutil
from llama_cpp import Llama


class PeakMemorySampler:
    """Background thread that tracks peak RSS (bytes) for the current process."""

    def __init__(self, process: psutil.Process, interval: float = 0.1) -> None:
        self._process = process
        self._interval = interval
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self.peak_rss = process.memory_info().rss

    def _run(self) -> None:
        while not self._stop.is_set():
            self.peak_rss = max(self.peak_rss, self._process.memory_info().rss)
            self._stop.wait(self._interval)

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        self._thread.join()


@dataclass
class InferenceResult:
    load_time: float
    first_token_latency: float | None
    total_time: float
    tokens: int
    tokens_per_sec: float | None
    peak_rss_bytes: int
    cpu_percent: float
    response: str


def run_inference(
    model_path: str,
    prompt: str,
    *,
    n_ctx: int = 2048,
    n_threads: int | None = None,
    max_tokens: int = 128,
) -> InferenceResult:
    """Load a GGUF model, run one prompt, and return timing/resource metrics."""
    process = psutil.Process()
    process.cpu_percent(
        interval=None
    )  # prime the counter; first call always returns 0.0

    mem_sampler = PeakMemorySampler(process)
    mem_sampler.start()

    load_start = time.perf_counter()
    llm = Llama(
        model_path=model_path,
        n_ctx=n_ctx,
        n_threads=n_threads,
        verbose=False,
    )
    load_time = time.perf_counter() - load_start

    infer_start = time.perf_counter()
    first_token_elapsed = None
    chunks = []
    for chunk in llm.create_chat_completion(
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        stream=True,
    ):
        delta = chunk["choices"][0]["delta"].get("content")
        if delta:
            if first_token_elapsed is None:
                first_token_elapsed = time.perf_counter() - infer_start
            chunks.append(delta)
    total_time = time.perf_counter() - infer_start

    mem_sampler.stop()
    cpu_percent = process.cpu_percent(interval=None)

    response = "".join(chunks)
    tokens = len(llm.tokenize(response.encode("utf-8"), add_bos=False))
    tokens_per_sec = tokens / total_time if tokens else None

    return InferenceResult(
        load_time=load_time,
        first_token_latency=first_token_elapsed,
        total_time=total_time,
        tokens=tokens,
        tokens_per_sec=tokens_per_sec,
        peak_rss_bytes=mem_sampler.peak_rss,
        cpu_percent=cpu_percent,
        response=response,
    )
