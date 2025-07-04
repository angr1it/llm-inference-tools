This document describes the project layout, main components and usage scenarios.

---

## 📁 Project Structure

```
/project-root
│
├── .env                         # Environment configuration (model paths, LORA, API)
├── docker-compose.yml          # Multi-service deployment with GPU support
├── Dockerfile.llm              # Image for llama.cpp / onnx runtime
├── Dockerfile.chat-ui          # Image for the LangChain Agent Chat UI
│
├── /models                     # Models (GGUF, ONNX, LoRA adapters)
├── /logs                       # Inference logs and RLHF scores
├── /data                       # Training datasets, DPO conversations
├── /lora                       # LoRA fine-tuning scripts and weights
├── /scripts                    # Utilities: quantize, convert, deploy
│
├── /llm-server                 # FastAPI interface switching llama.cpp/onnx
├── /chat-ui                    # LangChain Agent Chat UI (Next.js)
├── /mcp                        # MCP integration microservice
├── /langfuse                   # Tracing, RLHF export
└── /labelstudio                # Annotation config and templates
```

---

## 🔧 Components and Purpose

| Component                                   | Purpose |
| ------------------------------------------- | ------------------------------------------------------------ |
| **llm-server**                              | Inference via llama.cpp or onnxruntime. Supports SSE, auth, LoRA and config hot-reload |
| **chat-ui (LangChain Agent Chat UI)**       | ChatGPT-like web interface with reasoning tools and MCP support |
| **peft + LoRA**                             | Fine-tune the model on your data with adaptive quantisation |
| **Langfuse**                                | Collect and visualise logs, scores and RLHF metrics. Stores trace/token-level info |
| **Label Studio**                            | Annotation interface for pairwise comparison of answers (DPO/Reward datasets) |
| **MCP**                                     | Endpoints integration: plug in external tools, parsers, actions |
| **VS Code client (Continue.dev / CodeGPT)** | Developer interface inside the IDE with chat and tasks |
| **metrics layer**                           | Collect CPU/GPU usage, Prometheus / Grafana support |

---

## 🧪 Usage Scenarios

### 📌 1. ChatGPT-like development and testing

Use the LangChain Agent Chat UI together with the LLM server (llama.cpp or onnx).

```bash
docker compose up llm chat-ui
```

* The model is queried through the OpenAI API.
* The visual interface supports chain-of-thought prompts, tools and system messages.

---

### 📌 2. LoRA fine-tuning and model adaptation

Run fine-tuning on your data.

```bash
python scripts/finetune_lora.py --model Qwen3-8B --data data/train.jsonl
```

* The adapter is saved as `.gguf` and loaded via `--lora` or `LORA_PATHS`.
* The model applies the adapter without restarting the server.

---

### 📌 3. Collecting conversations for RLHF

All chat history is stored in Langfuse and/or JSONL.

* Thumbs/rating labels are kept for each pair.
* Data can be exported for DPO or TRLx.

```bash
docker compose up langfuse
```

---

### 📌 4. Answer annotation (A vs B)

Used to prepare reward or DPO datasets.

```bash
docker compose up labelstudio
```

* Dialogs are loaded from Langfuse or JSONL.
* Annotators choose the better of two answers.
* Export as TRLx-compatible JSONL.

---

### 📌 5. External actions (MCP)

Connect an external tool as a function (execute code, call an API, etc.).

```bash
curl http://mcp:9000/tool_call --data '{...}'
```

* MCP integration is available as an agent in LangChain.
* The response is proxied through the LLM and returned to the user.

---

### 📌 6. VS Code integration

Interact with the model from your editor using the local LLM API.

```env
OPENAI_API_BASE_URL=http://localhost:8000/v1
```

* Continue.dev or CodeGPT connect to llama.cpp/ONNX via the API.
* Sessions can be logged through Langfuse.

---

### 📌 7. Monitoring

Connect Prometheus / Grafana to track:

* CPU/GPU load
* latency and tokens
* RAM / disk usage

---

If needed, a `README.md` or `docker-compose.yaml` can describe these components in more detail.
