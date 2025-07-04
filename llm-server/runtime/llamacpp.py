import os
import subprocess
from typing import Iterable
from .base import BaseModelRuntime

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover - used for type checking only
    from llama_cpp import Llama  # noqa: F401
else:  # pragma: no cover - optional dependency
    Llama: Any = None


class LlamaCppRuntime(BaseModelRuntime):
    """Run inference via llama.cpp."""

    def _gguf_path(self) -> str:
        return os.path.join(self.cache_dir, "model.gguf")

    def prepare(self) -> None:
        os.makedirs(self.cache_dir, exist_ok=True)
        gguf = self._gguf_path()
        if not os.path.exists(gguf):
            # Example conversion from HuggingFace weights to GGUF
            subprocess.run([
                "python", "-m", "llama_cpp.convert", self.model_path, gguf
            ], check=False)
        if self.quantize:
            quantized = gguf.replace(".gguf", f".q{self.quantize}.gguf")
            if not os.path.exists(quantized):
                subprocess.run(["python", "-m", "llama_cpp.quantize", gguf, quantized, self.quantize], check=False)
            self.model_path = quantized
        else:
            self.model_path = gguf

    def load(self) -> None:
        if Llama is None:  # pragma: no cover - optional dependency
            raise ImportError("llama_cpp is not installed")
        self.model = Llama(model_path=self.model_path)  # type: ignore[misc]
        for adapter in self.lora_paths:
            if adapter:
                self.model.load_lora(adapter)  # type: ignore[attr-defined]

    def generate_stream(self, prompt: str) -> Iterable[str]:
        for chunk in self.model(prompt, stream=True):  # type: ignore[misc]
            yield chunk["choices"][0]["text"]
