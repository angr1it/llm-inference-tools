from .base import BaseModelRuntime
from .llamacpp import LlamaCppRuntime
from .onnxrt import OnnxRuntime


def create_runtime(
    backend: str,
    model_path: str,
    cache_dir: str | None = None,
    lora_paths: list[str] | None = None,
    quantize: str | None = None,
) -> BaseModelRuntime:
    runtime: BaseModelRuntime
    if backend == "llama.cpp":
        runtime = LlamaCppRuntime(model_path, cache_dir, lora_paths, quantize)
    elif backend == "onnxruntime":
        runtime = OnnxRuntime(model_path, cache_dir, lora_paths, quantize)
    else:
        raise ValueError(f"Unknown backend {backend}")
    runtime.prepare()
    runtime.load()
    return runtime

