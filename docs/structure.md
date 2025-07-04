Вот структурированный план по проекту с описанием архитектуры, компонентов и сценариев использования:

---

## 📁 Структура проекта

```
/project-root
│
├── .env                         # Конфигурация окружения (модель, LORA, API)
├── docker-compose.yml          # Мультисервисный запуск с GPU
├── Dockerfile.llm              # Образ для llama.cpp / onnx runtime
├── Dockerfile.chat-ui          # Образ для LangChain Agent Chat UI
│
├── /models                     # Модели (GGUF, ONNX, LoRA-адаптеры)
├── /logs                       # Журналы инференса и RLHF-оценок
├── /data                       # Обучающие датасеты, диалоги для DPO
├── /lora                       # Сценарии и веса LoRA-файнтюнинга
├── /scripts                    # Утилиты: quantize, convert, deploy
│
├── /llm-server                 # FastAPI-интерфейс, переключение llama.cpp/onnx
├── /chat-ui                    # LangChain Agent Chat UI (Next.js)
├── /mcp                        # MCP-интеграция как микросервис
├── /langfuse                   # Трассировки, экспорт RLHF
└── /labelstudio                # Конфиг и шаблоны аннотаций
```

---

## 🔧 Компоненты проекта и их назначение

| Компонент                                   | Назначение                                                                             |
| ------------------------------------------- | -------------------------------------------------------------------------------------- |
| **llm-server**                              | Инференс через llama.cpp или onnxruntime. Поддержка SSE, auth, LORA, config hot-reload |
| **chat-ui (LangChain Agent Chat UI)**       | Web-интерфейс в стиле ChatGPT с поддержкой reasoning, tools, MCP                       |
| **peft + LoRA**                             | Дообучение модели на своих данных с адаптивной квантизацией                            |
| **Langfuse**                                | Сбор и визуализация логов, оценок, метрик RLHF. Хранение trace/token-level info        |
| **Label Studio**                            | Интерфейс разметки для генерации парных сравнений ответов (DPO/Reward datasets)        |
| **MCP**                                     | Endpoints-интеграция: подключение внешних тулзов, парсеры, действия                    |
| **VS Code client (Continue.dev / CodeGPT)** | Интерфейс разработчика с подсветкой, чатом и задачами в IDE                            |
| **metrics layer**                           | Сбор GPU/CPU нагрузки, поддержка Prometheus / Grafana                                  |

---

## 🧪 Сценарии использования

### 📌 1. ChatGPT-подобная разработка и тестирование модели

> Использовать LangChain Agent Chat UI и LLM сервер (llama.cpp или onnx).

```bash
docker compose up llm chat-ui
```

* Модель запрашивается через OpenAI API.
* Визуальный интерфейс поддерживает chain-of-thought, tools, системные инструкции.

---

### 📌 2. LoRA-файнтюнинг и адаптация модели

> Пользователь дообучает Qwen 3 8B на своих данных.

```bash
python scripts/finetune_lora.py --model Qwen3-8B --data data/train.jsonl
```

* Сохраняется адаптер в `.gguf`, подключается через `--lora` или `LORA_PATHS`.
* При инференсе модель применяет адаптацию без рестарта сервера.

---

### 📌 3. Сбор диалогов для RLHF

> Вся история из чата сохраняется в Langfuse и/или JSONL:

* Метки thumbs/rating сохраняются для каждой пары.
* Данные экспортируются для DPO или TRLx.

```bash
docker compose up langfuse
```

---

### 📌 4. Разметка ответов (A vs B)

> Для подготовки reward-модели или DPO.

```bash
docker compose up labelstudio
```

* Загружаются диалоги (из Langfuse / JSONL).
* Аннотаторы выбирают лучший из двух ответов.
* Экспорт — JSONL в формате TRLx.

---

### 📌 5. Интеграция внешних действий (MCP)

> Подключение внешнего тулза как функции (выполнить код, позвонить API и т.п.)

```bash
curl http://mcp:9000/tool_call --data '{...}'
```

* MCP-интеграция доступна как агент в LangChain.
* Ответ проксируется через LLM и возвращается пользователю.

---

### 📌 6. VS Code интеграция

> Разработчик общается с моделью в редакторе, отправляя запросы на локальный LLM API.

```env
OPENAI_API_BASE_URL=http://localhost:8000/v1
```

* Continue.dev или CodeGPT подключаются к llama.cpp/ONNX через API.
* Сессии можно логгировать через Langfuse.

---

### 📌 7. Мониторинг

> Подключение Prometheus / Grafana для отслеживания:

* загруженности CPU/GPU,
* latency и токенов,
* RAM / disk usage.

---

Если хочешь, я могу сформировать `README.md` или `docker-compose.yaml`, отражающие эти компоненты.
