В одном open-source окружении можно собрать полный стек для работы с **Qwen 3 8B Reasoning**, включая LoRA-файнтюнинг, GPU-контейнер, чат-UI, REST-API и оба рантайма — **llama.cpp** (GGUF) и **ONNX Runtime**. Ниже приведены лучшие репозитории, приёмы оптимизации и пример Docker-композиции.

## 1 · Где взять модель

| Что                     | Репозиторий/пакет                                                                                                                                                                                       | Комментарий                                     |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------- |
| **Qwen 3 8B Reasoning** | `QwenLM/Qwen3` на GitHub ([github.com](https://github.com/QwenLM/Qwen3?utm_source=chatgpt.com)) / `Qwen/Qwen3-8B` на HF ([huggingface.co](https://huggingface.co/Qwen/Qwen3-8B?utm_source=chatgpt.com)) | FP16, GPTQ/AWQ и готовые GGUF-кванты (4-8 bit). |
| **GGUF конвертер**      | `convert.py` в llama.cpp ([github.com](https://github.com/abetlen/llama-cpp-python/blob/main/llama_cpp/server/__main__.py?utm_source=chatgpt.com))                                                      | Генерирует GGUF из HF-модели.                   |
| **ONNX чек-пойнт**      | экспорт через `optimum.onnxruntime` ([onnxruntime.ai](https://onnxruntime.ai/docs/genai/?utm_source=chatgpt.com))                                                                                       | Дает FP16 → INT8/INT4.                          |

## 2 · LoRA-файнтюнинг без GPU

| Способ                          | Репозиторий                                                                                                                                                    | Детали                                                    |
| ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| **LoRA на llama.cpp (CPU/GPU)** | встроенная утилита `finetune` ([reddit.com](https://www.reddit.com/r/LocalLLaMA/comments/16utjm0/finetune_lora_on_cpu_using_llamacpp/?utm_source=chatgpt.com)) | Генерирует адаптер `*.gguf`, применяемый флагом `--lora`. |
| **PEFT/LoRA для ONNX**          | `onnxruntime-genai` + PEFT                                                                                                                                     | Экспортируем LoRA-веса в ONNX, затем квантуем.            |

## 3 · GPU-контейнер разработки

*Базовая идея — один Dockerfile + compose:*

```dockerfile
FROM nvidia/cuda:12.4.0-cudnn-runtime-ubuntu22.04
RUN apt-get update && apt-get install -y git python3-dev python3-pip
RUN pip install --upgrade pip && \
    pip install llama-cpp-python[server] onnxruntime-gpu optimum[onnxruntime] \
               accelerate peft transformers fastapi uvicorn
# Скачаем модель при билде (по желанию):
RUN git clone https://huggingface.co/Qwen/Qwen3-8B /models/qwen3-8b
WORKDIR /app
CMD ["uvicorn", "llama_cpp.server:app", "--port", "8000"]
```

*Пример compose-файла добавит UI (Open-WebUI) и пробросит GPU:*

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

**Источники** — готовый GPU-образ для llama.cpp ([github.com](https://github.com/fboulnois/llama-cpp-docker?utm_source=chatgpt.com)) и обсуждение CUDA-Docker в llama-cpp-python ([github.com](https://github.com/abetlen/llama-cpp-python/discussions/1609?utm_source=chatgpt.com)).

## 4 · Чат-интерфейс

- Если нужен лёгкий standalone UI → **Open WebUI** ([github.com](https://github.com/open-webui/open-webui?utm_source=chatgpt.com), [docs.openwebui.com](https://docs.openwebui.com/?utm_source=chatgpt.com)).
- Минималистичный UI, написанный специально под llama.cpp → **MaggotHATE/Llama\_chat** ([github.com](https://github.com/MaggotHATE/Llama_chat?utm_source=chatgpt.com)) или форк Chatbot-UI ([github.com](https://github.com/yportne13/chatbot-ui-llama.cpp?utm_source=chatgpt.com)).
- Любой из UI подключается к back-энд-API совместимому с OpenAI.

## 5 · API-слой

| Рантайм          | Быстрый сервер                                                                                                                                                                                          |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **llama.cpp**    | `llama-cpp-python` уже содержит FastAPI-сервер (`python -m llama_cpp.server`) ([github.com](https://github.com/abetlen/llama-cpp-python/blob/main/llama_cpp/server/__main__.py?utm_source=chatgpt.com)) |
| **ONNX Runtime** | `onnxruntime-genai generate()` — генеративный API с KV-кешем ([onnxruntime.ai](https://onnxruntime.ai/docs/genai/?utm_source=chatgpt.com))                                                              |

Обе реализации поддерживают SSE-поток (чат-стрим) и заголовок `Authorization: Bearer`.

## 6 · Адаптеры и оптимизация

### llama.cpp

```bash
# GGUF-квант + полный offload
./llama-quantize qwen3-8b.gguf qwen3-8b.Q4_K_M.gguf q4_k_m
./llama-cli -m qwen3-8b.Q4_K_M.gguf -n_gpu_layers 99 -p "Привет!"
```

*Q4\_K\_M* укладывается ≈ 6 GB VRAM и даёт 80-100 tok/s на RTX 4090 ([github.com](https://github.com/abetlen/llama-cpp-python/blob/main/llama_cpp/server/__main__.py?utm_source=chatgpt.com)).

### ONNX

```python
from optimum.onnxruntime import ORTModelForCausalLM
m = ORTModelForCausalLM.from_pretrained("Qwen/Qwen3-8B", export=True)
m.save_pretrained("onnx/qwen3")
# динамическая INT8
from onnxruntime.quantization import quantize_dynamic
quantize_dynamic("onnx/qwen3/model.onnx","onnx/qwen3/int8.onnx")
```

INT8 снижает RAM в 4× и ускоряет inference ([onnxruntime.ai](https://onnxruntime.ai/docs/genai/?utm_source=chatgpt.com)).

---

### Готовое «меню» репозиториев

| Задача         | Репозиторий                                                                                                                                               |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Модель и веса  | QwenLM/Qwen3 ([github.com](https://github.com/QwenLM/Qwen3?utm_source=chatgpt.com))                                                                       |
| GGUF-конвертер | llama.cpp `convert.py` ([github.com](https://github.com/abetlen/llama-cpp-python/blob/main/llama_cpp/server/__main__.py?utm_source=chatgpt.com))          |
| LoRA (CPU)     | llama.cpp finetune guide ([reddit.com](https://www.reddit.com/r/LocalLLaMA/comments/16utjm0/finetune_lora_on_cpu_using_llamacpp/?utm_source=chatgpt.com)) |
| GPU Dockerfile | fboulnois/llama-cpp-docker ([github.com](https://github.com/fboulnois/llama-cpp-docker?utm_source=chatgpt.com))                                           |
| Чат-UI         | open-webui/open-webui ([github.com](https://github.com/open-webui/open-webui?utm_source=chatgpt.com))                                                     |
| ONNX Gen-AI    | onnxruntime-genai ([onnxruntime.ai](https://onnxruntime.ai/docs/genai/?utm_source=chatgpt.com))                                                           |
| FastAPI server | llama-cpp-python ([github.com](https://github.com/abetlen/llama-cpp-python/blob/main/llama_cpp/server/__main__.py?utm_source=chatgpt.com))                |

## 7 · Что дальше

1. **Соберите контейнер**, запустив `docker compose up -d`. При использовании старых версий Docker добавьте флаг `--gpus all`.
2. **Разместите модель** (GGUF или ONNX‑INT8) в томе `/models` и, при необходимости, укажите путь к ней переменной `MODEL_PATH`.
3. **Откройте UI** по адресу `http://localhost:3000` (Open WebUI) и сразу начните чат или задайте ключ API, если требуется.
4. **Подключайте/меняйте LoRA‑адаптеры**: передайте флаги `--lora adapter1.gguf,adapter2.gguf` или переменную окружения `LORA_PATHS`, затем перезапустите сервис `llm`.
5. **Следите за ресурсами**: используйте `docker stats`/`nvidia-smi` — если VRAM > 80 %, уменьшайте `n_gpu_layers` или переходите на более жёсткую квантизацию.
6. **Обновляйте модель** заменой файлов в `/models` и командой `docker compose restart llm`; UI автоматически переподключится.

