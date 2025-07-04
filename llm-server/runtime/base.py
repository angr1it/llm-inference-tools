import os
from typing import Iterable, Optional


class BaseModelRuntime:
    """Abstract base runtime for any inference backend."""

    def __init__(self, model_path: str, cache_dir: str | None = None,
                 lora_paths: Optional[list[str]] = None, quantize: str | None = None):
        self.model_path = model_path
        self.cache_dir = cache_dir or model_path
        self.lora_paths = lora_paths or []
        self.quantize = quantize
        self.model = None

    def prepare(self) -> None:
        """Prepare model files for loading (download/convert/quantize)."""
        raise NotImplementedError

    def load(self) -> None:
        """Load the model into memory."""
        raise NotImplementedError

    def generate_stream(self, prompt: str) -> Iterable[str]:
        """Generate a sequence of text chunks."""
        raise NotImplementedError
