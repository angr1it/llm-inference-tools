## Functional Requirements

### 1. Model and inference

* Load **Qwen 3 8B Reasoning** from HuggingFace with configuration through `.env`.
* Supported formats: FP16, GGUF, ONNX.
* Two inference modes:
  * **llama.cpp** (default) with quantisation, `--lora`, `n_gpu_layers` and memory mapping.
  * **ONNX Runtime GenAI** with INT8/INT4 support, CUDA Execution Provider and the `generate()` API.
* Switching runtimes via environment variables.
* Support for contexts beyond 32k (YaRN / rope-scaling).

### 2. Fine-tuning

* LoRA fine-tuning support:
  * llama.cpp built-in `finetune` → `.gguf` adapter
  * `peft + transformers` → export to ONNX
* Quantisation-aware training.
* Adapter management with `--lora` or the `LORA_PATHS` variable; dynamic loading.
* Works on CPU and GPU.

### 3. Chat interface: LangChain Agent Chat UI

* Web interface similar to ChatGPT.
* Multi-role chat (User, Assistant, Tools).
* Chain-of-Thought, streaming tokens and history logging.
* Function and tool support.
* Compatible with the OpenAI API (`/v1/chat/completions`).

### 4. RLHF / Feedback / Metrics

* Logging in JSONL format.
* Integration with:
  * **Langfuse** for tracing, rating and dataset export.
  * **Label Studio** with a pairwise ranking template.
* Annotation options (thumbs, rating scale).
* Dataset preparation for DPO, TRLx, PPO.
* Ability to export logs through the UI.

### 5. API and server

* FastAPI interface with:
  * SSE (`stream=true`)
  * Token-based auth (`Authorization: Bearer`)
  * MCP-compatible `tool_calls`
* REST integration with external services (including LangChain and Langfuse).

### 6. MCP integration

* Support for the MCP SDK (Python).
* MCP endpoint available as an internal service or a callback inside the LangChain Agent.
* Option to connect external MCP tools in the UI.

---

## ⚙️ Technical Requirements

### .env and configuration variables

* `MODEL_PATH` — path to the model (HF or local)
* `RUNTIME_BACKEND=llama.cpp|onnx`
* `LORA_PATHS=/models/lora/*.gguf`
* `OPENAI_API_BASE_URL=http://llm:8000/v1`
* `LANGFUSE_API_KEY=...`

### Containerisation

* Docker image based on `nvidia/cuda:12.x` with:
  * `llama-cpp-python[server]`
  * `onnxruntime-gpu`, `optimum`, `transformers`, `peft`
  * `fastapi`, `uvicorn`, `langchain`
* `docker-compose` with GPU passthrough:
  * volumes: `/models`, `/logs`
  * services: `llm`, `chat-ui`, `langfuse`, `labelstudio`

### Resources

* CPU with AVX2 (preferably AVX-VNNI/AMX)
* GPU ≥ 6 GB VRAM
* RAM ≥ 16 GB for models larger than 7B

---

## 🧪 Extras

* VS Code extensions: **Continue.dev**, **CodeGPT** with an OpenAI-compatible API.
* Metrics: integration with Prometheus / Grafana, log GPU/CPU usage (`nvidia-smi`, `docker stats`).
* Hot reload of the model and LoRA adapters without stopping the service.

---

## 🧱 Architecture and Components

| Component | Purpose |
| --------- | ------- |
| `llm` | inference server (llama.cpp / onnxruntime) with OpenAI API |
| `chat-ui` | LangChain Agent Chat UI for interacting with the model |
| `langfuse` | conversation tracing, scoring and RLHF preparation |
| `labelstudio` | pairwise dialog annotation for reward models |
| `mcp` | MCP tools and an endpoint for connecting to the agent |
| `peft-tools` | scripts for LoRA training and quantisation |
| `vs-code-ext` | IDE client with model support |

Each of these components can be launched as part of a single `docker-compose` stack if needed.
