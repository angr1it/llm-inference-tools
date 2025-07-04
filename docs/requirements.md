## Функциональные требования

### 1. Модель и инференс

* Загрузка модели **Qwen 3 8B Reasoning** (из HuggingFace), конфигурируемой через `.env`.
* Поддержка форматов: FP16, GGUF, ONNX.
* Два режима инференса:

  * **llama.cpp** (по умолчанию): GGUF, квантизация, поддержка `--lora`, `n_gpu_layers`, `mmap`.
  * **ONNX Runtime GenAI**: поддержка INT8/INT4, CUDA Execution Provider, `generate()` API.
* Возможность переключения между рантаймами через переменные окружения.
* Поддержка контекста >32k (YaRN / rope-scaling).

### 2. Fine-tuning / дообучение

* Поддержка LoRA fine-tuning:

  * llama.cpp встроенный `finetune` → `.gguf`
  * `peft + transformers` → ONNX export
* Возможность квантизации (quantization-aware training).
* Управление адаптерами: `--lora`, переменная `LORA_PATHS`, динамическая подгрузка.
* Поддержка CPU и GPU.

### 3. Чат-интерфейс: LangChain Agent Chat UI

* Веб-интерфейс в стиле ChatGPT.
* Мультиролевой чат (User, Assistant, Tools).
* Chain-of-Thought, потоковые токены, логирование истории.
* Поддержка функций и "tools".
* Интеграция с OpenAI API интерфейсом (`/v1/chat/completions`).

### 4. RLHF / Feedback / Метрики

* Логирование в формате JSONL.
* Интеграция с:

  * **Langfuse**: трассировка, рейтинг, экспорт датасетов.
  * **Label Studio**: шаблон pairwise ranking.
* Возможность аннотаций (thumbs, шкала оценок).
* Подготовка датасетов для DPO, TRLx, PPO.
* Возможность экспорта логов через интерфейс UI.

### 5. API и серверная часть

* FastAPI-интерфейс:

  * SSE (`stream=true`)
  * Авторизация по токену (`Authorization: Bearer`)
  * MCP-compatible `tool_calls`
* Возможность REST-интеграции с внешними сервисами (включая LangChain, Langfuse).

### 6. MCP интеграция

* Поддержка MCP SDK (Python).
* MCP endpoint доступен как внутренний сервис или в виде callback внутри LangChain Agent.
* Возможность подключения внешних MCP-инструментов в UI.

---

## ⚙️ Технические требования

### .env и переменные конфигурации

* `MODEL_PATH` — путь к модели (HF или локально)
* `RUNTIME_BACKEND=llama.cpp|onnx`
* `LORA_PATHS=/models/lora/*.gguf`
* `OPENAI_API_BASE_URL=http://llm:8000/v1`
* `LANGFUSE_API_KEY=...`

### Контейнеризация

* Docker образ на `nvidia/cuda:12.x` базе:

  * `llama-cpp-python[server]`
  * `onnxruntime-gpu`, `optimum`, `transformers`, `peft`
  * `fastapi`, `uvicorn`, `langchain`
* `docker-compose` с GPU пробросом:

  * volumes: `/models`, `/logs`
  * сервисы: `llm`, `chat-ui`, `langfuse`, `labelstudio`

### Ресурсы

* CPU с AVX2 (лучше AVX-VNNI/AMX)
* GPU ≥ 6 GB VRAM
* RAM ≥ 16 GB (для моделей >7B)

---

## 🧪 Дополнительно

* VS Code расширения: **Continue.dev**, **CodeGPT** с поддержкой OpenAI-compatible API.
* Метрики: интеграция с Prometheus / Grafana, логирование GPU/CPU (`nvidia-smi`, `docker stats`).
* Горячая перезагрузка модели и LoRA адаптеров без остановки сервиса.

---

## 🧱 Архитектура и компоненты

| Компонент     | Назначение                                              |
| ------------- | ------------------------------------------------------- |
| `llm`         | сервер инференса (llama.cpp / onnxruntime) с OpenAI API |
| `chat-ui`     | LangChain Agent Chat UI для взаимодействия с моделью    |
| `langfuse`    | трассировка диалогов, сбор оценок, RLHF подготовка      |
| `labelstudio` | аннотация pairwise диалогов для reward моделей          |
| `mcp`         | MCP-инструменты и endpoint для подключения к агенту     |
| `peft-tools`  | скрипты дообучения LoRA и квантизации                   |
| `vs-code-ext` | клиент внутри IDE с поддержкой модели                   |

Если нужно, каждый из этих компонентов разворачивается в рамках одного `docker-compose`.

---
