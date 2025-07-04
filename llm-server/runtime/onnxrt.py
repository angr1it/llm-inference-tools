from typing import Iterable
from .base import BaseModelRuntime

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover - used for type checking only
    from optimum.onnxruntime import ORTModelForCausalLM  # noqa: F401
    from transformers import AutoTokenizer  # noqa: F401
else:  # pragma: no cover - optional dependency
    ORTModelForCausalLM: Any = None
    AutoTokenizer: Any = None


class OnnxRuntime(BaseModelRuntime):
    def prepare(self) -> None:  # For demo, assume model already prepared
        pass

    def load(self) -> None:
        if ORTModelForCausalLM is None or AutoTokenizer is None:  # pragma: no cover
            raise ImportError("onnxruntime and transformers are required")
        self.model = ORTModelForCausalLM.from_pretrained(self.model_path)  # type: ignore[misc]
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)  # type: ignore[misc]

    def generate_stream(self, prompt: str) -> Iterable[str]:
        inputs = self.tokenizer(prompt, return_tensors="pt")  # type: ignore[misc]
        for token_id in self.model.generate(**inputs, max_new_tokens=64)[0]:  # type: ignore[attr-defined]
            yield self.tokenizer.decode(token_id, skip_special_tokens=True)  # type: ignore[misc]
