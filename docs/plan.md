# Deployment Plan

This document outlines how to prepare a working stack for **Qwen 3 8B Reasoning**. The goal is to run the model in either `llama.cpp` or `ONNX Runtime`, fine-tune adapters with LoRA, expose a chat UI and REST API, and collect logs for RLHF.

## 1 · Where to get the model

| Item | Repository/Package | Notes |
| ---- | ------------------ | ----- |
| **Qwen 3 8B Reasoning** | [QwenLM/Qwen3](https://github.com/QwenLM/Qwen3) / [Qwen/Qwen3-8B](https://huggingface.co/Qwen/Qwen3-8B) | FP16 checkpoints, GPTQ/AWQ and ready GGUF quants |
| **GGUF converter** | [`convert.py` from llama.cpp](https://github.com/abetlen/llama-cpp-python/blob/main/llama_cpp/server/__main__.py) | Creates GGUF from a HF model |
| **ONNX checkpoint** | Export via `optimum.onnxruntime` | FP16 → INT8/INT4 |

## 2 · LoRA fine-tuning without a GPU

| Approach | Repository | Details |
| -------- | ---------- | ------- |
| **LoRA with llama.cpp** | built-in `finetune` ([discussion](https://www.reddit.com/r/LocalLLaMA/comments/16utjm0/finetune_lora_on_cpu_using_llamacpp/)) | Produces `*.gguf` adapter to be used with `--lora` |
| **PEFT/LoRA for ONNX** | `onnxruntime-genai` + PEFT | Export LoRA weights to ONNX and then quantize |

## 3 · GPU development container

A simple approach is to use one Dockerfile with compose:

```dockerfile
FROM nvidia/cuda:12.4.0-cudnn-runtime-ubuntu22.04
RUN apt-get update && apt-get install -y git python3-dev python3-pip
RUN pip install --upgrade pip && \
    pip install llama-cpp-python[server] onnxruntime-gpu optimum[onnxruntime] \
               accelerate peft transformers fastapi uvicorn
# Optionally download the model during build
RUN git clone https://huggingface.co/Qwen/Qwen3-8B /models/qwen3-8b
WORKDIR /app
CMD ["uvicorn", "llama_cpp.server:app", "--port", "8000"]
```

Example compose snippet to add a UI (Open WebUI) and expose the GPU:

```yaml
services:
  llm:
    build: .
    deploy:
      resources:
        reservations:
          devices:
            - capabilities: [gpu]
  webui:
    image: openwebui/open-webui:latest
    ports: ["3000:8080"]
    environment:
      - OPENAI_API_BASE_URL=http://llm:8000/v1
```

Useful references: [llama-cpp-docker](https://github.com/fboulnois/llama-cpp-docker) and the CUDA-Docker discussion in [llama-cpp-python](https://github.com/abetlen/llama-cpp-python/discussions/1609).

## 4 · Chat interface

- Lightweight standalone UI → [Open WebUI](https://github.com/open-webui/open-webui)
- Minimal UI tailored for llama.cpp → [MaggotHATE/Llama_chat](https://github.com/MaggotHATE/Llama_chat) or a fork of Chatbot-UI
- Any of these UIs connect to an OpenAI-compatible backend API

## 5 · API layer

| Runtime | Quick server |
| ------- | ------------ |
| **llama.cpp** | `llama-cpp-python` already includes a FastAPI server (`python -m llama_cpp.server`) |
| **ONNX Runtime** | `onnxruntime-genai generate()` provides a generation API with KV cache |

Both implementations support SSE (streaming chat) and the `Authorization: Bearer` header.

## 6 · Adapters and optimisation

### llama.cpp

```bash
# GGUF quant + full offload
./llama-quantize qwen3-8b.gguf qwen3-8b.Q4_K_M.gguf q4_k_m
./llama-cli -m qwen3-8b.Q4_K_M.gguf -n_gpu_layers 99 -p "Hello!"
```

`Q4_K_M` fits into ~6 GB of VRAM and yields 80-100 tok/s on an RTX 4090.

### ONNX

```python
from optimum.onnxruntime import ORTModelForCausalLM
m = ORTModelForCausalLM.from_pretrained("Qwen/Qwen3-8B", export=True)
m.save_pretrained("onnx/qwen3")
from onnxruntime.quantization import quantize_dynamic
quantize_dynamic("onnx/qwen3/model.onnx", "onnx/qwen3/int8.onnx")
```

INT8 reduces RAM usage by 4× and speeds up inference.

---

### Helpful repositories

| Task | Repository |
| ---- | ---------- |
| Model and weights | [QwenLM/Qwen3](https://github.com/QwenLM/Qwen3) |
| GGUF converter | [llama.cpp `convert.py`](https://github.com/abetlen/llama-cpp-python/blob/main/llama_cpp/server/__main__.py) |
| LoRA (CPU) | [llama.cpp finetune guide](https://www.reddit.com/r/LocalLLaMA/comments/16utjm0/finetune_lora_on_cpu_using_llamacpp/) |
| GPU Dockerfile | [fboulnois/llama-cpp-docker](https://github.com/fboulnois/llama-cpp-docker) |
| Chat UI | [open-webui/open-webui](https://github.com/open-webui/open-webui) |
| ONNX Gen-AI | [onnxruntime-genai](https://onnxruntime.ai/docs/genai/) |
| FastAPI server | [llama-cpp-python](https://github.com/abetlen/llama-cpp-python/blob/main/llama_cpp/server/__main__.py) |

## 7 · Next steps

1. **Build the container** with `docker compose up -d`. Older Docker versions may require `--gpus all`.
2. **Place the model** (GGUF or ONNX-INT8) in `/models` and set `MODEL_PATH` if needed.
3. **Open the UI** at `http://localhost:3000` and start chatting or set an API key if required.
4. **Attach or switch LoRA adapters** via `--lora adapter1.gguf,adapter2.gguf` or the `LORA_PATHS` variable and restart the `llm` service.
5. **Watch your resources** using `docker stats` or `nvidia-smi`. If VRAM > 80%, reduce `n_gpu_layers` or choose a smaller quantisation.
6. **Update the model** by replacing files in `/models` and running `docker compose restart llm`; the UI will reconnect automatically.
